from fastapi import APIRouter, Depends, Response
from fastapi_csrf_protect import CsrfProtect
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.modules.auth.schemas import UserAuth
from app.modules.auth.service import get_me_data, logout_data, register_user_data, login_user_data
from app.modules.auth.models import User
from app.api.deps import get_current_user

router = APIRouter()

logger = structlog.get_logger(__name__)

@router.post('/login')
async def login_user(response: Response, data: UserAuth,  csrf_protect: CsrfProtect = Depends(), db: AsyncSession = Depends(get_db)):
    logger.info("login_user", username=data.username)
    return await login_user_data(response, data, csrf_protect, db)

@router.post('/register')
async def register_user(data: UserAuth, db: AsyncSession = Depends(get_db)):
    return await register_user_data(data, db)

@router.get('/me')
async def get_me(current_user: User =  Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_me_data(current_user.id, db)

@router.post('/logout')
async def logout(response: Response, csrf_protect: CsrfProtect = Depends()):
    return await logout_data(response, csrf_protect)