from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class CategorySchema(BaseModel):
    id: int
    name: str
    eda_id: str
    

class CategoryOut(BaseModel):
    name: str


class IngredientSchema(BaseModel):
    name: str
    is_allergen: bool = False


class RecipeSchema(BaseModel):
    id: int
    name: str
    url: str
    cooking_time: int
    portions: int = Field(ge=1, default=1, description="Количество порций")
    ingredients: List[IngredientSchema] = []
    category: Optional[CategoryOut] = None


class RecipeUpdate(BaseModel):
    name: Optional[str] = None
    cooking_time: Optional[int] = None


class UserSchema(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool = True


class CommentSchema(BaseModel):
    author: str
    com_text: str


class PostSchema(BaseModel):
    title: str
    post_text: str
    comments: List[CommentSchema] = []


class UserCreate(BaseModel):
    username: str
    password: str
    email: str

    @field_validator("username")
    def check_username(cls, v):
        if len(v) < 3:
            raise ValueError("Имя слишком короткое (минимум 3 символа)")
        if "admin" in v.lower():
            raise ValueError(f"Нельзя использовать имя admin")
        return v


class UserOut(BaseModel):
    username: str
    email: str

class ProductCreate(BaseModel):
    name: str
    price: int

class ProductOut(BaseModel):
    name: str
    price: int
    tax: int
