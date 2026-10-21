from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import User
from app.api.deps import get_current_user
from app.core.database import get_db
from app.modules.stats.service import get_by_category_data, get_monthly_data, get_summary_data
from app.modules.stats.schemas import ByCategoryRead, MonthlyRead
from app.modules.categories.models import TransactionType

router = APIRouter()

@router.get("/summary")
async def get_summary(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_summary_data(current_user.id, db)

@router.get("/monthly", response_model=list[MonthlyRead])
async def get_monthly(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_monthly_data(current_user.id, db)

@router.get("/by-category", response_model=list[ByCategoryRead])
async def get_by_category(type: TransactionType, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_by_category_data(type, current_user.id, db)