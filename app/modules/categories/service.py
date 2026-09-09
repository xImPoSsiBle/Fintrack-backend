from fastapi import HTTPException, status
from sqlalchemy import or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.categories.models import Category, TransactionType
from app.modules.categories.schemas import CategoryCreate


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