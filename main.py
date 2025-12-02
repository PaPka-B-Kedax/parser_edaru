from sqlalchemy import select, text
from sqlalchemy.orm import selectinload
from fastapi import FastAPI, Depends, HTTPException
from routers import recipes, users, categories
from schemas import PostSchema, ProductCreate, ProductOut
from database import new_session 


app = FastAPI()

app.include_router(recipes.router)
app.include_router(users.router)
app.include_router(categories.router)


fake_items_db = [
    {"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"},
    {"item_name": "Ham"}, {"item_name": "Spam"}, {"item_name": "Eggs"},
]


@app.get("/")
async def root():
    return {"message": "Hello World!", "student": "You"}

@app.get("/sum")
async def sum_():
    return {"message": 50+50}

@app.get("/mult/{a}/{b}")
async def mult(a: int, b: int):
    return {"results": a*b}

@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]

@app.post("/blog/")
async def create_post(post: PostSchema):
    print(f"Пост '{post.title}' успешно опубликован с {len(post.comments)} комментариями.")
    return f"Пост '{post.title}' успешно опубликован с {len(post.comments)} комментариями.", {
        "Заголовок": post.title,
        "Текст": post.post_text,
        "Первый комментарий": post.comments[0].com_text if post.comments else None
    }


@app.post("/products", response_model=ProductOut)
async def create_product(product: ProductCreate):
    tax = product.price * 0.2
    if product.price < 0:
        raise HTTPException(status_code=404, detail="Цена не может быть отрицательной")
    
    return product.dict() | {"tax": tax} 