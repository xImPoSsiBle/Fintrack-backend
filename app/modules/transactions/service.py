from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.transactions.models import Transaction
from app.modules.transactions.schemas import TransactionCreate
from app.modules.categories.models import Category

async def get_transactions_data(current_user_id: int, db: AsyncSession):
    result = await db.execute(select(
        Category.name.label("name"),
        Transaction
        )
        .join(Category, Transaction.category_id == Category.id)
        .where(Transaction.user_id == current_user_id)
        .order_by(Transaction.date.desc())
        )

    return [
        {
            "name": row.name,
            "transaction": row.Transaction,
        }
        for row in result.all()
    ]

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

async def delete_transaction_data(transaction_id: int, current_user_id: int,  db: AsyncSession):
    transaction = await db.scalar(
        select(Transaction).where(Transaction.id == transaction_id, Transaction.user_id == current_user_id)
    )

    if transaction is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Транзакция не найдена')

    await db.delete(transaction)
    await db.commit()