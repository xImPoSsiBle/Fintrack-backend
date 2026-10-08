from decimal import Decimal
from datetime import date
from pydantic import BaseModel, ConfigDict
from app.modules.categories.models import TransactionType


class TransactionData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    type: TransactionType
    amount: Decimal
    date: date
    description: str | None

class TransactionRead(BaseModel):
    name: str
    transaction: TransactionData

class TransactionCreate(BaseModel):
    category_id: int
    type: TransactionType
    amount: Decimal
    date: date
    description: str | None = None