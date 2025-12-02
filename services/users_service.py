from schemas import UserCreate

async def register_user_logic(user: UserCreate):
    print(f"Сохранение пользователя {user.username} с паролем {user.password}")
    return user