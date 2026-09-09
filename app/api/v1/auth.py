from fastapi import APIRouter, Depends, Response
from fastapi_csrf_protect import CsrfProtect
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.modules.auth.schemas import UserAuth
from app.modules.auth.service import register_user_data, login_user_data

router = APIRouter()

logger = structlog.get_logger(__name__)

@router.post('/login')
async def login_user(response: Response, data: UserAuth,  csrf_protect: CsrfProtect = Depends(), db: AsyncSession = Depends(get_db)):
    logger.info("login_user", username=data.username)
    return await login_user_data(response, data, csrf_protect, db)

@router.post('/register')
async def register_user(data: UserAuth, db: AsyncSession = Depends(get_db)):
    return await register_user_data(data, db)