from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.period import Period
from app.api.deps import get_current_user, verify_csrf
from app.modules.auth.models import User
from app.modules.transactions.service import delete_transaction_data, get_transactions_data, create_transaction_data
from app.modules.transactions.schemas import TransactionCreate, TransactionRead


router = APIRouter()

@router.get("", response_model=list[TransactionRead])
async def get_transactions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    search: str | None = Query(None, max_length=100),
    period: Period = Query(Period.all),
):
    return await get_transactions_data(current_user.id, db, search, period)


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_csrf)])
async def create_transaction(
    data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_transaction_data(data, current_user.id, db)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(verify_csrf)])
async def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await delete_transaction_data(transaction_id, current_user.id, db)