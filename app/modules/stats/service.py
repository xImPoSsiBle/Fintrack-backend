from sqlalchemy import case, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.transactions.models import Transaction
from app.modules.categories.models import TransactionType, Category


async def get_summary_data(current_user_id: int, db: AsyncSession):
    result = await db.execute(select(
            func.coalesce(
                func.sum(case((Transaction.type == "income", Transaction.amount), else_=0)), 0
            ).label("income"),
            func.coalesce(
                func.sum(case((Transaction.type == "expense", Transaction.amount), else_=0)), 0
            ).label("expense")
        ).where(Transaction.user_id == current_user_id)
    )

    row = result.one()

    return {
        "income": row.income,
        "expense": row.expense,
        "balance": row.income - row.expense
    }

async def get_monthly_data(current_user_id: int, db: AsyncSession):
    result = await db.execute(select(
            func.to_char(
                func.date_trunc("month", Transaction.date),
                "YYYY-MM"
            ).label("month"),
            func.coalesce(
                func.sum(case((Transaction.type == "income", Transaction.amount), else_=0)), 0
            ).label("income"),
            func.coalesce(
                func.sum(case((Transaction.type == "expense", Transaction.amount), else_=0)), 0
            ).label("expense")
        )
        .where(Transaction.user_id == current_user_id)
        .group_by("month")
        .order_by("month")
    )

    return result.all()


async def get_by_category_data(type: TransactionType, current_user_id: int, db: AsyncSession):
    result = await db.execute(select(
            Category.name.label("name"),
            func.coalesce(
                func.sum(Transaction.amount), 0
            ).label("value")
        )
        .join(Category, Transaction.category_id == Category.id)
        .where(Transaction.user_id == current_user_id, Transaction.type == type)
        .group_by("name")
    )

    return result.all()