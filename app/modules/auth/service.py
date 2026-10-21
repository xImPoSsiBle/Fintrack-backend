from fastapi import HTTPException, Response, status
from fastapi_csrf_protect import CsrfProtect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.schemas import UserAuth
from app.modules.auth.models import User
from app.modules.auth.utils import create_access_token, create_refresh_token, hash_password, verify_password
from app.core.config import settings

COOKIE_PARAMS = dict(httponly=True, secure=settings.cookie_secure, samesite="lax")

async def login_user_data(response: Response, data: UserAuth, csrf_protect: CsrfProtect, db: AsyncSession):
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Неверный логин или пароль")

    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    csrf_protect.set_csrf_cookie(signed_token, response)

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    response.set_cookie(key="access_token", value=access_token, **COOKIE_PARAMS)

    response.set_cookie(key="refresh_token", value=refresh_token, **COOKIE_PARAMS)

    return {
        "user": {
            "id": user.id,
            "username": user.username
        },
        "csrf_token": csrf_token
    }

async def register_user_data(data: UserAuth, db: AsyncSession):
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()

    if user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Пользователь с таким именем уже существует")

    hashed = hash_password(data.password)

    new_user = User(username=data.username, hashed_password=hashed)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

async def get_me_data(current_user_id: User, db: AsyncSession):
    user = await db.scalar(
        select(User)
        .where(User.id == current_user_id)
        )

    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Такого пользователя не существует")

    return {"user": {
        "id": user.id,
        "username": user.username
    }}

async def logout_data(response: Response, csrf_protect: CsrfProtect):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    csrf_protect.unset_csrf_cookie(response)
    return {"detail": "Выход выполнен"}