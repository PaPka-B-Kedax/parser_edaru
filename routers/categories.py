from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from database import new_session
from models_edaru import Category
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