from fastapi import HTTPException, status
from sqlalchemy import or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.modules.categories.models import Category, TransactionType
from app.modules.categories.schemas import CategoryCreate, CategoryUpdate

logger = structlog.get_logger(__name__)

async def get_categories_data(db: AsyncSession):
    result = await db.execute(select(Category))
    return result.scalars().all()

async def get_category_by_type_data(type: TransactionType, current_user_id: int | None, db: AsyncSession):
    if current_user_id is not None:
        condition = or_(Category.user_id == current_user_id, Category.user_id.is_(None))
    else:
        condition = Category.user_id.is_(None)
    
    result = await db.execute(select(Category).where(
        Category.type == type, condition
    ))

    return result.scalars().all()

async def create_category_data(data: CategoryCreate, current_user_id: int, db: AsyncSession):
    result = await db.execute(select(Category).where(
        or_(Category.user_id == current_user_id, Category.user_id.is_(None)), 
        func.lower(Category.name) == data.name.lower()))

    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Такая категория уже существует")

    new_category = Category(name=data.name, type=data.type, user_id=current_user_id)

    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)

    return new_category

async def update_category_data(category_id: int, data: CategoryUpdate, current_user_id: int, db: AsyncSession):
    category = await db.scalar(select(Category).where(Category.id == category_id, Category.user_id == current_user_id))

    if category is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Категория не найдена")

    changes = {}

    if data.name is not None:
        existing = await db.scalar(select(Category).where(
            or_(Category.user_id == current_user_id, Category.user_id.is_(None)),
            func.lower(Category.name) == data.name.lower(),
            Category.id != category_id
        ))

        if existing:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Такая категория уже существует")
        changes["name"] = {"old": category.name, "new": data.name}
        category.name = data.name

    if data.type is not None:
        changes["type"] = {"old": category.type.value, "new": data.type.value}
        category.type = data.type

    if changes:
        logger.info("category_updated", category_id=category_id, user_id=current_user_id, changes=changes)

    await db.commit()
    await db.refresh(category)

    return category
    