import enum

from sqlalchemy import ForeignKey, Index, UniqueConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

class TransactionType(str, enum.Enum):
    income = "income"
    expense = "expense"

class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("id", "type", name="uq_category_id_type"),
        Index(
            "uq_category_user_name_lower",
            "user_id", text("lower(name)"),
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    type: Mapped[TransactionType]
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)