from pydantic import BaseModel, ConfigDict


class MonthlyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    month: str
    income: int
    expense: int

class ByCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    value: int