import httpx
import asyncio
import logging
import argparse
from sqlalchemy import select

from config import CONCURRENCY, HEADERS
from parser_core import get_total_pages, fetch_page_data
from database import new_session
from models_edaru import Category, Recipe, Ingredient


CATEGORY_NAMES = {
    528: "Бульоны",
    520: "Завтраки",
    531: "Закуски",
    532: "Напитки",
    533: "Основные блюда",
    534: "Паста и Пицца",
    535: "Ризотто",
    536: "Салаты",
    537: "Соусы и маринады",
    538: "Супы",
    539: "Сэндвичи",
    541: "Выпечка и десерты",
    1685: "Заготовки"
}


def setup_logging():
    # Заглушка
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    # Логгер
    logger = logging.getLogger() 
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        logger.handlers.clear()

    # Консоль
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
    console_handler.setFormatter(console_format)
    
    # Файл
    file_handler = logging.FileHandler(
        "parser.log", 
        mode='w', 
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(file_format)
    
    # проверка
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


async def save_recipe_to_db(session, recipe_data, category_eda_id):
    query_cat = select(Category).where(Category.eda_id == str(category_eda_id))
    results_cat = await session.execute(query_cat)
    category_obj = results_cat.scalar_one_or_none()
    
    if not category_obj:
        cat_name = CATEGORY_NAMES.get(int(category_eda_id), f"Category {category_eda_id}")
        logging.info(f"Создаю новую категорию: {cat_name} (ID: {category_eda_id})")

        category_obj = Category(
            eda_id=str(category_eda_id),
            name=cat_name
        )
        session.add(category_obj)


    query_recipe = select(Recipe).where(Recipe.eda_id == str(recipe_data['id']))
    results_recipe = await session.execute(query_recipe)
    existing_recipe = results_recipe.scalar_one_or_none()

    if existing_recipe:
        logging.info(f"Рецепт {recipe_data['name']} (ID: {recipe_data['id']}) уже есть. Пропускаем.")
        return
    
    new_recipe = Recipe(
        eda_id=str(recipe_data['id']),
        name=recipe_data['name'],
        url=recipe_data['url'],
        cooking_time=recipe_data['cooking_time'],
        portions=recipe_data['portions']
    )

    new_recipe.category = category_obj

    if recipe_data.get('ingredients'):
        for ing_name in recipe_data['ingredients']:
            new_ing = Ingredient(name=ing_name)
            new_recipe.ingredients.append(new_ing)

    session.add(new_recipe)
    await session.commit()
    logging.info(f"Добавлен: {new_recipe.name} (+ {len(new_recipe.ingredients)} ингред.)")


async def process_category(category_id, limit_pages, client, semaphore):
    cat_name = CATEGORY_NAMES.get(int(category_id), str(category_id))
    logging.info(f"Начинаю обработку категории: {cat_name} (ID: {category_id})")

    logging.info(f"--- Узнаеём сколько страниц ---")
    pages = await get_total_pages(client, semaphore, category_id)
    if pages <= 1:
        logging.warning("Разведчик не смог получить > 1 страницы. Возможно, ошибка или мало данных.")
        if pages == 0:
            return
            
    logging.info(f"Всего страниц: {pages}")

    if limit_pages > 0 and limit_pages < pages:
        pages = limit_pages
        logging.warning(f"Ограничение на количество страниц: {pages}")

    logging.info(f"--- Генерация {pages} задач ---")
    tasks = []
    for i in range(1, pages + 1):
        tasks.append(fetch_page_data(client, semaphore, i, category_id))

    logging.info(f"--- Запускаю {len(tasks)} задач параллельно ---")
    pred_results = await asyncio.gather(*tasks)

    final_results = [item for sublist in pred_results if sublist for item in sublist]

    logging.info(f"Категория {cat_name}: получено {len(final_results)} рецептов. Запись в БД...")

    if final_results:
        async with new_session() as session:
            for item in final_results:
                try:
                    await save_recipe_to_db(session, item, category_id)
                except Exception as e:
                    logging.error(f"Ошибка при сохранении {item.get('name')}: {e}")
                    await session.rollback()

    logging.info(f"Категория {cat_name} успешно обработана.")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Асинхронный парсер Eda.ru")

    parser.add_argument(
        "-c", "--category_id",
        type=int,
        default= 538,
        help="ID одной категории (если не выбран флаг --all)"
        )
    
    parser.add_argument(
        "-l", "--limit",
        type=int,
        default=0,
        help="Ограничение на количество страниц для парсинга"
        )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Парсить все категории"
    )

    return parser.parse_args()


async def main(category_id, limit_pages, run_all):
    setup_logging()

    timeout_config = httpx.Timeout(10.0, read=20.0)
    semaphore = asyncio.Semaphore(CONCURRENCY)

    async with httpx.AsyncClient(headers=HEADERS, timeout=timeout_config, follow_redirects=True) as client:
        if run_all:
            logging.info(f"Запущен парсинг всех категорий ({len(CATEGORY_NAMES)} шт.)")
            for cat_id in CATEGORY_NAMES.keys():
                await process_category(cat_id, limit_pages, client, semaphore)
                await asyncio.sleep(2)
        else:
            await process_category(category_id, limit_pages, client, semaphore)
    
    logging.info("Парсер завершил работу.")
    

if __name__ == "__main__":
    args = parse_arguments()
    
    try:
        asyncio.run(main(
        category_id=args.category_id,
        limit_pages=args.limit,
        run_all=args.all
        ))
    except KeyboardInterrupt:
        print("Остановлено пользователем.")