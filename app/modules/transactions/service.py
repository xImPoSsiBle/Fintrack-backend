from fastapi import HTTPException, status
from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import structlog

from app.modules.transactions.models import Transaction
from app.modules.transactions.schemas import TransactionCreate
from app.modules.categories.models import Category
from app.core.period import Period, get_date_from

logger = structlog.get_logger(__name__)

async def get_transactions_data(current_user_id: int, db: AsyncSession, search: str | None = None, period: Period = Period.all):
    query = (
        select(Category.name.label("name"),Transaction)
        .join(Category, Transaction.category_id == Category.id)
        .where(Transaction.user_id == current_user_id)
        .order_by(Transaction.date.desc(), Transaction.id.desc())
        )

    date_from = get_date_from(period)

    if date_from:
        query = query.where(Transaction.date >= date_from)

    if search:
       query = query.where(or_(
            Category.name.icontains(search, autoescape=True),
            Transaction.description.icontains(search, autoescape=True),
        ))

    result = await db.execute(query)

    return [
        {
            "name": row.name,
            "transaction": row.Transaction,
        }
        for row in result.all()
    ]

async def create_transaction_data(data: TransactionCreate, current_user_id: int, db: AsyncSession):
    category = await db.scalar(
        select(Category).where(
            Category.id == data.category_id, 
            Category.type == data.type,
            or_(Category.user_id == current_user_id, Category.user_id.is_(None))
            )
    )

    if category is None:
        logger.warning("transaction_invalid_category", user_id=current_user_id, category_id=data.category_id)
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

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        logger.warning("transaction_category_gone", user_id=current_user_id, category_id=data.category_id)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Категория не найдена или не соответствует типу транзакции")
    await db.refresh(new_transaction)

    logger.info(
        "transaction_created",
        transaction_id=new_transaction.id,
        user_id=current_user_id,
        type=category.type.value,
        amount=str(data.amount),
    )
    return new_transaction

async def delete_transaction_data(transaction_id: int, current_user_id: int,  db: AsyncSession):
    transaction = await db.scalar(
        select(Transaction).where(Transaction.id == transaction_id, Transaction.user_id == current_user_id)
    )

    if transaction is None:
        logger.warning("transaction_not_found", transaction_id=transaction_id, user_id=current_user_id)
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Транзакция не найдена')

    await db.delete(transaction)
    await db.commit()

    logger.info("transaction_deleted", transaction_id=transaction_id, user_id=current_user_id)