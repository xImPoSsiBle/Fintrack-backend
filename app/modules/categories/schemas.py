from pydantic import BaseModel, ConfigDict

from app.modules.categories.models import TransactionType

class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: TransactionType
    user_id: int | None

class CategoryCreate(BaseModel):
    name: str
    type: TransactionType

class CategoryUpdate(BaseModel):
    name: str | None = None
    type: TransactionType | None = None