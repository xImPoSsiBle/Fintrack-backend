from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user
from app.modules.auth.models import User
from app.modules.transactions.service import get_transactions_data, create_transaction_data
from app.modules.transactions.schemas import TransactionCreate, TransactionRead


router = APIRouter()

@router.get("", response_model=list[TransactionRead])
async def get_transactions(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_transactions_data(current_user.id, db)

@router.post("")
async def create_transaction(data: TransactionCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await create_transaction_data(data, current_user.id, db)