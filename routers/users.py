from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database import new_session
from schemas import UserSchema, UserCreate, UserOut
from services.users_service import register_user_logic


router = APIRouter(prefix="/users", tags=["Users"])

users_db = {"ivan": "secret"}

@router.post("/register", response_model=UserOut)
async def register_user(user: UserCreate):
    return await register_user_logic(user)

@router.get("/me")
async def read_user_me():
    return {"user_id": "current_user"}

@router.get("/{user_id}")
async def read_user(user_id: int):
    return {"user_id": user_id, "type": str(type(user_id))}

@router.get("/login/{username}")
async def login(username: str, password: str):
    if username not in users_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if password != users_db[username]:
        raise HTTPException(status_code=404, detail="Неверный пароль")
    return {"message": "Успешный вход"}