from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import User
from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.period import Period
from app.modules.stats.service import get_by_category_data, get_monthly_data, get_summary_data
from app.modules.stats.schemas import ByCategoryRead, MonthlyRead, SummaryRead
from app.modules.categories.models import TransactionType

router = APIRouter()

@router.get("/summary", response_model=SummaryRead)
async def get_summary(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db), period: Period = Query(Period.all)):
    return await get_summary_data(current_user.id, db, period)

@router.get("/monthly", response_model=list[MonthlyRead])
async def get_monthly(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db), period: Period = Query(Period.all)):
    return await get_monthly_data(current_user.id, db, period)

@router.get("/by-category", response_model=list[ByCategoryRead])
async def get_by_category(type: TransactionType, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db), period: Period = Query(Period.all)):
    return await get_by_category_data(type, current_user.id, db, period)