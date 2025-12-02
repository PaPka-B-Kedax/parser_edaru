from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from typing import List
from database import Base


class Category(Base):
    __tablename__="categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    eda_id: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    recipes: Mapped[List["Recipe"]] = relationship(back_populates="category")

    def __repr__(self):
        return f"<Category(name='{self.name}')>"


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    eda_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(Text)
    cooking_time: Mapped[int | None] = mapped_column()
    portions: Mapped[int | None] = mapped_column()
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))
    category: Mapped["Category"] = relationship(back_populates="recipes")

    ingredients: Mapped[List["Ingredient"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan"    
    
    )

    def __repr__(self):
        return f"<Recipe(name='{self.name}', eda_id='{self.eda_id}')>"
    

class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"))
    recipe: Mapped["Recipe"] = relationship(back_populates="ingredients")

    def __repr__(self):
        return f"<Ingredient(name='{self.name}')>"
