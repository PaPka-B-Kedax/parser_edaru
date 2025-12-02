from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from models_edaru import Recipe, Ingredient
from schemas import RecipeSchema
import random

async def create_recipe_logic(recipe: RecipeSchema, db: AsyncSession):
    fake_eda_id = str(random.randint(100000, 999999))

    new_recipe = Recipe(
        eda_id=fake_eda_id,
        name=recipe.name,
        url=recipe.url,
        cooking_time=recipe.cooking_time or 0,
        portions=recipe.portions
    )

    for ing_schema in recipe.ingredients:
        new_ing = Ingredient(name=ing_schema.name)
        new_recipe.ingredients.append(new_ing)

    db.add(new_recipe)
    await db.commit()
    await db.refresh(new_recipe, attribute_names=["ingredients"])
    return new_recipe


async def get_all_recipes(
        db: AsyncSession,
        skip: int = 0, 
        limit = 10, 
        search: str = None, 
        ingredient: str = None, 
        category_id: int = None
):
    query = select(Recipe).options(selectinload(Recipe.ingredients), joinedload(Recipe.category))

    if search:
        query = query.where(Recipe.name.ilike(f"%{search}%"))

    if ingredient:
        query = query.where(Recipe.ingredients.any(Ingredient.name.ilike(f"%{ingredient}%")))

    if category_id:
        query = query.where(Recipe.category_id == category_id)
    
    query = query.offset(skip).limit(limit)
    res = await db.execute(query)
    return res.scalars().all()