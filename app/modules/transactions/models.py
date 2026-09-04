from decimal import Decimal
from datetime import date
from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.modules.categories.models import TransactionType

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    category_id: Mapped[int]
    type: Mapped[TransactionType]
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    date: Mapped[date]
    description: Mapped[str | None]