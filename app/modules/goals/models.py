from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import VARCHAR, CheckConstraint, DateTime, ForeignKey, Index, Numeric, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Goal(Base):
    __tablename__ = "goals"
    __table_args__ = (
        CheckConstraint("target_amount > 0", name="ck_goals_target_amount_positive"),
        Index(
            "uq_goal_user_name_lower",
            "user_id", text("lower(name)"),
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(VARCHAR(100))
    target_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    deadline: Mapped[date]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class GoalContribution(Base):
    __tablename__ = 'goal_contributions'
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_goal_contributions_amount_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    goal_id: Mapped[int] = mapped_column(ForeignKey("goals.id", ondelete="CASCADE"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())