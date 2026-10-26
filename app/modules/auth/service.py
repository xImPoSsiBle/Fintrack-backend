from fastapi import HTTPException, Response, status
from fastapi_csrf_protect import CsrfProtect
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.modules.auth.schemas import UserAuth
from app.modules.auth.models import User
from app.modules.auth.utils import create_access_token, create_refresh_token, hash_password, verify_password
from app.core.config import settings

logger = structlog.get_logger(__name__)

COOKIE_PARAMS = dict(httponly=True, secure=settings.cookie_secure, samesite="lax")

def _issue_csrf(response: Response, csrf_protect: CsrfProtect) -> str:
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    csrf_protect.set_csrf_cookie(signed_token, response)
    return csrf_token

def _user_out(user: User) -> dict:
    return {"id": user.id, "username": user.username}

async def login_user_data(response: Response, data: UserAuth, csrf_protect: CsrfProtect, db: AsyncSession):
    user = await db.scalar(select(User).where(User.username == data.username))

    if not user or not verify_password(data.password, user.hashed_password):
        logger.warning("login_failed", username=data.username)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Неверный логин или пароль")

    csrf_token = _issue_csrf(response, csrf_protect)

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    response.set_cookie(key="access_token", value=access_token, **COOKIE_PARAMS)

    response.set_cookie(key="refresh_token", value=refresh_token, **COOKIE_PARAMS)

    logger.info("login_success", user_id=user.id)
    return {"user": _user_out(user), "csrf_token": csrf_token}

async def register_user_data(data: UserAuth, db: AsyncSession):
    exists = await db.scalar(select(User.id).where(User.username == data.username))

    if exists:
        logger.warning("register_failed_username_taken", username=data.username)
        raise HTTPException(status.HTTP_409_CONFLICT, "Пользователь с таким именем уже существует")

    new_user = User(username=data.username, hashed_password=hash_password(data.password))

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        logger.warning("register_failed_username_taken", username=data.username)
        raise HTTPException(status.HTTP_409_CONFLICT, "Пользователь с таким именем уже существует")

    await db.refresh(new_user)
    logger.info("register_success", user_id=new_user.id)
    return _user_out(new_user)

async def get_me_data(
    response: Response, current_user_id: int, csrf_protect: CsrfProtect, db: AsyncSession
):
    user = await db.get(User, current_user_id)

    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Такого пользователя не существует")

    csrf_token = _issue_csrf(response, csrf_protect)
    return {"user": _user_out(user), "csrf_token": csrf_token}

async def logout_data(response: Response, csrf_protect: CsrfProtect):
    response.delete_cookie("access_token", **COOKIE_PARAMS)
    response.delete_cookie("refresh_token", **COOKIE_PARAMS)
    csrf_protect.unset_csrf_cookie(response)
    logger.info("logout")
    return {"detail": "Выход выполнен"}