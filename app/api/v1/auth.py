from fastapi import APIRouter, Depends, Request, Response
from fastapi_csrf_protect import CsrfProtect
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.database import get_db
from app.core.redis import get_redis
from app.modules.auth.schemas import UserAuth
from app.modules.auth.service import get_me_data, logout_data, refresh_data, register_user_data, login_user_data
from app.modules.auth.models import User
from app.api.deps import get_current_user, verify_csrf

router = APIRouter()

@router.post('/login')
async def login_user(
    request: Request,
    response: Response, 
    data: UserAuth,  
    csrf_protect: CsrfProtect = Depends(), 
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    ip = request.client.host if request.client else "unknown"
    return await login_user_data(response, ip, data, csrf_protect, db, redis)

@router.post('/register')
async def register_user(data: UserAuth, db: AsyncSession = Depends(get_db)):
    return await register_user_data(data, db)

@router.post('/refresh')
async def refresh(
    response: Response, 
    request: Request, 
    db: AsyncSession = Depends(get_db), 
    csrf_protect: CsrfProtect = Depends(),
    redis: Redis = Depends(get_redis)
):
    return await refresh_data(response, request, db, csrf_protect, redis)

@router.get('/me')
async def get_me(
    response: Response,
    current_user: User = Depends(get_current_user),
    csrf_protect: CsrfProtect = Depends(),
    db: AsyncSession = Depends(get_db),
    ):
    return await get_me_data(response, current_user.id, csrf_protect, db)

@router.post('/logout', dependencies=[Depends(verify_csrf)])
async def logout(
    response: Response, 
    request: Request,
    csrf_protect: CsrfProtect = Depends(), 
    redis: Redis = Depends(get_redis)
):
    return await logout_data(response, request, csrf_protect, redis)