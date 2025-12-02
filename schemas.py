from pydantic import BaseModel, Field, computed_field
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
    @computed_field
    def cooking_time_str(self) -> str:
        if self.cooking_time < 60:
            return f"{self.cooking_time} мин"
        else:
            a = self.cooking_time // 60
            b = self.cooking_time - (a * 60)
            return f"{a} ч {b} мин"
    portions: int = Field(ge=1, default=1, description="Количество порций")
    ingredients: List[IngredientSchema] = []
    category: Optional[CategoryOut] = None


class RecipeUpdate(BaseModel):
    name: Optional[str] = None
    cooking_time: Optional[int] = None