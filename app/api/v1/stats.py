from fastapi import APIRouter, Depends, Query
from pydantic import TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.modules.auth.models import User
from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.period import Period
from app.core.redis import get_redis
from app.core.cache import cache_get, cache_set, stats_version, STATS_TTL
from app.modules.stats.service import get_by_category_data, get_monthly_data, get_summary_data
from app.modules.stats.schemas import ByCategoryRead, MonthlyRead, SummaryRead
from app.modules.categories.models import TransactionType

router = APIRouter()

monthly_adapter = TypeAdapter(list[MonthlyRead])
by_category_adapter = TypeAdapter(list[ByCategoryRead])

@router.get("/summary", response_model=SummaryRead)
async def get_summary(
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db), 
    redis: Redis = Depends(get_redis),
    period: Period = Query(Period.all)
):
    ver = await stats_version(redis, current_user.id)
    if ver is not None:
        key = f"stats:summary:{current_user.id}:v{ver}:{period.value}"

        if cached := await cache_get(redis, key):
            return SummaryRead.model_validate_json(cached)

    data = await get_summary_data(current_user.id, db, period)
    result = SummaryRead.model_validate(data)

    if ver is not None:
        await cache_set(redis, key, result.model_dump_json(), STATS_TTL)

    return result

@router.get("/monthly", response_model=list[MonthlyRead])
async def get_monthly(
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis), 
    period: Period = Query(Period.all)
):
    ver = await stats_version(redis, current_user.id)

    if ver is not None:
        key = f"stats:monthly:{current_user.id}:v{ver}:{period.value}"

        if cached := await cache_get(redis, key):
            return monthly_adapter.validate_json(cached)

    data = await get_monthly_data(current_user.id, db, period)
    result = monthly_adapter.validate_python(data, from_attributes=True)

    if ver is not None:
        await cache_set(redis, key, monthly_adapter.dump_json(result), STATS_TTL)

    return result

@router.get("/by-category", response_model=list[ByCategoryRead])
async def get_by_category(
    type: TransactionType, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis), 
    period: Period = Query(Period.all)
):
    ver = await stats_version(redis, current_user.id)

    if ver is not None:
        key = f"stats:by-category:{current_user.id}:v{ver}:{type.value}:{period.value}"

        if cached := await cache_get(redis, key):
            return by_category_adapter.validate_json(cached)

    data = await get_by_category_data(type, current_user.id, db, period)
    result = by_category_adapter.validate_python(data, from_attributes=True)

    if ver is not None:
        await cache_set(redis, key, by_category_adapter.dump_json(result), STATS_TTL)
    
    return result