from decimal import Decimal

from pydantic import BaseModel, ConfigDict

class SummaryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    income: Decimal
    expense: Decimal
    balance: Decimal

class MonthlyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    month: str
    income: int
    expense: int

class ByCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    value: int