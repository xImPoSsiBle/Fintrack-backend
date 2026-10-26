from fastapi import APIRouter, Depends, Response
from fastapi_csrf_protect import CsrfProtect
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.schemas import UserAuth
from app.modules.auth.service import get_me_data, logout_data, register_user_data, login_user_data
from app.modules.auth.models import User
from app.api.deps import get_current_user, verify_csrf

router = APIRouter()

@router.post('/login')
async def login_user(response: Response, data: UserAuth,  csrf_protect: CsrfProtect = Depends(), db: AsyncSession = Depends(get_db)):
    return await login_user_data(response, data, csrf_protect, db)

@router.post('/register')
async def register_user(data: UserAuth, db: AsyncSession = Depends(get_db)):
    return await register_user_data(data, db)

@router.get('/me')
async def get_me(
    response: Response,
    current_user: User = Depends(get_current_user),
    csrf_protect: CsrfProtect = Depends(),
    db: AsyncSession = Depends(get_db),
    ):
    return await get_me_data(response, current_user.id, csrf_protect, db)

@router.post('/logout', dependencies=[Depends(verify_csrf)])
async def logout(response: Response, csrf_protect: CsrfProtect = Depends()):
    return await logout_data(response, csrf_protect)