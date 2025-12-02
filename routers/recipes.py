from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database import new_session
from models_edaru import Category, Recipe, Ingredient
from schemas import RecipeSchema, RecipeUpdate, CategorySchema
from services.recipes_service import create_recipe_logic, get_all_recipes


router = APIRouter(prefix="/recipes", tags=["Recipes"])


async def get_db():
    async with new_session() as session:
        yield session


@router.get("/", response_model=List[RecipeSchema])
async def read_recipes(
    skip: int = 0, 
    limit: int = 10, 
    search: Optional[str] = None, 
    ingredient: Optional[str] = None,
    category_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    recipes = await get_all_recipes(db, skip=skip, limit=limit, search=search, ingredient=ingredient, category_id=category_id)
    return recipes


@router.get("/{recipe_id}")
async def read_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Recipe).where(Recipe.id == recipe_id).options(selectinload(Recipe.ingredients))
    res = await db.execute(query)
    recipe = res.scalars().one_or_none()
    return recipe


@router.post("/", status_code=201)
async def create_recipe_db(recipe: RecipeSchema, db: AsyncSession = Depends(get_db)):
    try:
        new_recipe = await create_recipe_logic(recipe, db)

        return {
            "status": "created",
            "id": new_recipe.id,
            "name": new_recipe.name,
            "ingredients_count": len(new_recipe.ingredients)
        }
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    

@router.patch("/{recipe_id}")
async def update_recipe(recipe_id: int, recipe_update: RecipeUpdate, db: AsyncSession = Depends(get_db)):
    query = select(Recipe).where(Recipe.id == recipe_id)
    res = await db.execute(query)
    recipe = res.scalars().one_or_none()

    if not recipe:
        raise HTTPException(status_code=404, detail="Рецепт не найден")
    
    update_data = recipe_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(recipe, key, value)

    await db.commit()
    await db.refresh(recipe)
    return recipe


@router.delete("/{recipe_id}", status_code=204)
async def delete_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Recipe).where(Recipe.id == recipe_id)
    res = await db.execute(query)
    recipe = res.scalars().one_or_none()

    if not recipe:
        raise HTTPException(status_code=404, detail="Рецепт не найден")
    
    await db.delete(recipe)
    await db.commit()
    return None

@router.delete("/categories/{category_id}", status_code=204)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Category).where(Category.id == category_id)
    res = await db.execute(query)
    category = res.scalars().one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    
    query_count = select(func.count(Recipe.id)).where(Recipe.category_id == category_id)
    res_count = await db.execute(query_count)
    recipes_count = res_count.scalar()

    if recipes_count > 0:
        raise HTTPException(status_code=400, detail="Нельзя удалить категорию, в которой есть рецепты.")
    
    await db.delete(category)
    await db.commit()
    return None