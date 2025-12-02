import httpx
import asyncio
import jmespath
import json
import math
import logging

from config import API_URL, LIMIT, QUERY_STRING


async def get_total_pages(client, semaphore, category_id):
    payload = {
        "operationName": "recipesInfinityScrollList",
        "variables": {
            "first": LIMIT,
            "offset": 0,
            "recipeCategoryId": f"{category_id}",
            "sortDirection": "DESC",
            "sortField": "RELEVANCE"
        },
        "query": QUERY_STRING
    }

    async with semaphore:
        logging.info("Разведчик: Запрашиваю количество страниц...")
        try:
            response = await client.post(API_URL, json=payload)
            response.raise_for_status()
            logging.info(f"Разведчик: Сервер ответил {response.status_code}")

            data = response.json()

            total_count_path = "data.recipes.totalCount"
            total_count = jmespath.search(total_count_path, data)

            if isinstance(total_count, int):
                total_pages = math.ceil(total_count / LIMIT)
                logging.info(f"Разведчик: Найдено товаров: {total_count}, Лимит: {LIMIT}, Страниц: {total_pages}")
                return total_pages
            else:
                logging.error(f"Разведчик: Не найден 'totalCount' по пути '{total_count_path}'.")
                return 1

        except httpx.HTTPStatusError as e:
            logging.error(f"Разведчик: HTTP Ошибка {e.response.status_code}.")
            return 1
        except Exception as e:
            logging.error(f"Разведчик: Неизвестная ошибка: {e}")
            return 1


async def fetch_page_data(client, semaphore, page_num, category_id):
    offset = (page_num - 1) * LIMIT
    payload = {
        "operationName": "recipesInfinityScrollList",
        "variables": {
            "first": LIMIT,
            "offset": offset, 
            "recipeCategoryId": f"{category_id}",
            "sortDirection": "DESC",
            "sortField": "RELEVANCE"
        },
        "query": QUERY_STRING
    }

    async with semaphore:
        logging.info(f"Начинаю парсить страницу №{page_num}...")
        try:
            response = await client.post(API_URL, json=payload)
            response.raise_for_status()
            logging.info(f"Сервер ответил: {response.status_code}")

            data = response.json()
            logging.debug(f"Стр {page_num}: Получен 'сырой' JSON: {data}")

            recipes_list_path = "data.recipes.nodes || []"
            recipes_list = jmespath.search(recipes_list_path, data)

            page_results = []

            id_path = "id"
            name_path = "name"
            url_path = "relativeUrl"
            cooking_time_path = "cookingTime"
            portions_path = "portionsCount"
            ingredients_path = "composition[].ingredient.name"
            
            for recipe in recipes_list:
                clean_item = {
                    "id": jmespath.search(id_path, recipe),
                    "name": jmespath.search(name_path, recipe),
                    "url": f"https://eda.ru{jmespath.search(url_path, recipe)}",
                    "cooking_time": jmespath.search(cooking_time_path, recipe),
                    "portions": jmespath.search(portions_path, recipe),
                    "ingredients": jmespath.search(ingredients_path, recipe)
                }
                page_results.append(clean_item)

            logging.info(f"Страница: {page_num}, Успешно обработано рецептов: {len(page_results)}")
            return page_results

        except httpx.TimeoutException:
            logging.warning(f"Страница: {page_num}: Сервер не отвечает (Timeout)")
            return []
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP-ошибка: {e}", exc_info=True)
            return []
        except httpx._exceptions.ConnectError as e:
            logging.error(f"Ошибка подключения: {e}")
            return []
        except jmespath.exceptions.JMESPathError as e:
            logging.error(f"Ошибка JMESPath: {e}")
            return []
        except json.JSONDecodeError:
            logging.error("Ошибка: Сервер вернул не JSON")
            return []
        except Exception as e:
            logging.error(f"Страница {page_num} - Ошибка: {e}", exc_info=True)
            return []