from sqlalchemy import case, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.period import Period, get_date_from
from app.modules.transactions.models import Transaction
from app.modules.categories.models import TransactionType, Category


async def get_summary_data(current_user_id: int, db: AsyncSession, period: Period = Period.all,):
    query = (select(
                func.coalesce(
                    func.sum(case((Transaction.type == "income", Transaction.amount), else_=0)), 0
                ).label("income"),
                func.coalesce(
                    func.sum(case((Transaction.type == "expense", Transaction.amount), else_=0)), 0
                ).label("expense")
            )
            .where(Transaction.user_id == current_user_id)
        )

    date_from = get_date_from(period)
    if date_from:
        query = query.where(Transaction.date >= date_from)

    result = await db.execute(query)

    row = result.one()

    return {
        "income": row.income,
        "expense": row.expense,
        "balance": row.income - row.expense
    }

async def get_monthly_data(current_user_id: int, db: AsyncSession, period: Period = Period.all,):
    query = (select(
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

    date_from = get_date_from(period)
    if date_from:
        query = query.where(Transaction.date >= date_from)

    result = await db.execute(query)

    return result.all()


async def get_by_category_data(type: TransactionType, current_user_id: int, db: AsyncSession, period: Period = Period.all,):
    query = (select(
                Category.name.label("name"),
                func.coalesce(
                    func.sum(Transaction.amount), 0
                ).label("value")
        )
        .join(Category, Transaction.category_id == Category.id)
        .where(Transaction.user_id == current_user_id, Transaction.type == type)
        .group_by("name")
    )

    date_from = get_date_from(period)
    if date_from:
        query = query.where(Transaction.date >= date_from)

    result = await db.execute(query)

    return result.all()