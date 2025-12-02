from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from database import new_session
from models_edaru import Category, Recipe
from schemas import CategorySchema


router = APIRouter(prefix="/categories", tags=["Categories"])


async def get_db():
    async with new_session() as session:
        yield session


@router.get("/", response_model=List[CategorySchema])
async def get_categories(db: AsyncSession = Depends(get_db)):
    query = select(Category)
    res = await db.execute(query)
    return res.scalars().all()


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