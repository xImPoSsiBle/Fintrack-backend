from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, computed_field
from pydantic.alias_generators import to_camel

class GoalResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: int
    name: str
    target_amount: float
    current_amount: float
    deadline: date

    @computed_field
    @property
    def percent(self) -> int:
        return min(
            int((self.current_amount/self.target_amount)*100), 100
            )

    @computed_field
    @property
    def remaining(self) -> float:
        return round(max(
            (self.target_amount-self.current_amount), 0
        ), 2)


class GoalCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    target_amount: Decimal = Field(gt=0)
    deadline: date

class ContributionCreate(BaseModel):
    amount: Decimal = Field(gt=0)
