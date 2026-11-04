from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.api.deps import get_current_user, get_optional_current_user, verify_csrf

from app.core.database import get_db
from app.modules.categories.service import create_category_data, delete_category_data, get_categories_data, get_category_by_type_data, update_category_data
from app.modules.categories.schemas import CategoryCreate, CategoryRead, CategoryUpdate
from app.modules.categories.models import TransactionType
from app.modules.auth.models import User

router = APIRouter()

logger = structlog.get_logger(__name__)

@router.get("", response_model=list[CategoryRead])
async def get_categories(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_categories_data(current_user.id, db)

@router.get("/{type}", response_model=list[CategoryRead])
async def get_category_by_type(type: TransactionType, current_user: User | None = Depends(get_optional_current_user), db: AsyncSession = Depends(get_db)):
    current_user_id = current_user.id if current_user else None
    return await get_category_by_type_data(type, current_user_id, db)

@router.post(
    "",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_csrf)],
)
async def create_category(data: CategoryCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    logger.info("create_new_catogory", user_id=current_user.id)
    return await create_category_data(data, current_user.id, db)

@router.patch(
    "/{category_id}",
    response_model=CategoryRead,
    dependencies=[Depends(verify_csrf)],
)
async def update_category(category_id: int, data: CategoryUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await update_category_data(category_id, data, current_user.id, db)

@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_csrf)],
)
async def delete_category(category_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await delete_category_data(category_id, current_user.id, db)