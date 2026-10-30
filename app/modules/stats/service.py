from sqlalchemy import case, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.period import Period, get_date_from
from app.modules.transactions.models import Transaction
from app.modules.categories.models import TransactionType, Category


def _filters(user_id: int, period: Period) -> list:
    conditions = [Transaction.user_id == user_id]
    date_from = get_date_from(period)
    if date_from:
        conditions.append(Transaction.date >= date_from)
    return conditions

def _sum_of(type_: TransactionType):
    return func.coalesce(
        func.sum(Transaction.amount).filter(Transaction.type == type_), 0
    )

async def get_summary_data(current_user_id: int, db: AsyncSession, period: Period = Period.all,):
    result = await db.execute(
        select(
                _sum_of(TransactionType.income).label("income"),
                _sum_of(TransactionType.expense).label("expense"),
        ).where(*_filters(current_user_id, period))
    )

    row = result.one()

    return {
        "income": row.income,
        "expense": row.expense,
        "balance": row.income - row.expense
    }

async def get_monthly_data(current_user_id: int, db: AsyncSession, period: Period = Period.all,):
    month = month = func.to_char(Transaction.date, "YYYY-MM").label("month")
    result = await db.execute(
        select(
            month,
            _sum_of(TransactionType.income).label("income"),
            _sum_of(TransactionType.expense).label("expense"),
        )
        .where(*_filters(current_user_id, period))
        .group_by(month)
        .order_by(month)
    )

    return result.all()


async def get_by_category_data(type: TransactionType, current_user_id: int, db: AsyncSession, period: Period = Period.all,):
    total = func.sum(Transaction.amount).label("value")

    result = await db.execute(
        select(
                Category.name.label("name"), total
        )
        .join(Category, Transaction.category_id == Category.id)
        .where(*_filters(current_user_id, period), Transaction.type == type)
        .group_by(Category.id, Category.name)
        .order_by(total.desc())
    )

    return result.all()