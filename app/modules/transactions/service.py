from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.transactions.models import Transaction
from app.modules.transactions.schemas import TransactionCreate
from app.modules.categories.models import Category

async def get_transactions_data(current_user_id: int, db: AsyncSession):
    result = await db.execute(select(Transaction).where(Transaction.user_id == current_user_id))

    return result.scalars().all()

async def create_transaction_data(data: TransactionCreate, current_user_id: int, db: AsyncSession):
    category = await db.scalar(
        select(Category).where(Category.id == data.category_id, Category.type == data.type)
    )

    if category is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Категория не найдена или не соответствует типу транзакции")

    new_transaction = Transaction(
        user_id = current_user_id,
        category_id = category.id,
        type = category.type,
        amount = data.amount,
        date = data.date,
        description = data.description
    )

    db.add(new_transaction)

    await db.commit()
    await db.refresh(new_transaction)
    return new_transaction