from fastapi import FastAPI
from routers import recipes, categories


app = FastAPI(
    title="Eda.ru Recipe Aggregator",
    description="API для сбора и анализа кулинарных рецептов.",
    version="1.0.0"     
)


app.include_router(recipes.router)
app.include_router(categories.router)


@app.get("/")
async def root():
    return {"message": "Добро пожаловать в Eda.ru Parser API. Перейдите в /docs для получения информации о Swagger UI"}