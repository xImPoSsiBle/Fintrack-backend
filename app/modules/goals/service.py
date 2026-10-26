from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.modules.goals.models import Goal, GoalContribution
from app.modules.goals.schemas import ContributionCreate, GoalCreate, GoalResponse
from app.modules.stats.service import get_summary_data

logger = structlog.get_logger(__name__)

async def get_available_data(current_user_id: int, db: AsyncSession) -> Decimal:
    summary = await get_summary_data(current_user_id, db)

    saved = await db.scalar(
        select(func.coalesce(func.sum(GoalContribution.amount), 0))
        .join(Goal, Goal.id == GoalContribution.goal_id)
        .where(Goal.user_id == current_user_id)
    )

    return summary["balance"] - saved

async def get_goals_data(current_user_id: int, db: AsyncSession):
    result = await db.execute(
        select(Goal, func.coalesce(
            func.sum(GoalContribution.amount), 0
        ).label("current_amount"))
        .where(Goal.user_id == current_user_id)
        .outerjoin(GoalContribution, GoalContribution.goal_id == Goal.id)
        .group_by(Goal.id)
        .order_by(Goal.created_at)
        )

    return [
    GoalResponse(
        id=goal.id,
        name=goal.name,
        target_amount=goal.target_amount,
        current_amount=current,
        deadline=goal.deadline,
    )
    for goal, current in result.all()
]

async def create_goal_data(data: GoalCreate, current_user_id: int, db: AsyncSession):
    existing = await db.scalar(
        select(Goal)
        .where(Goal.user_id == current_user_id, func.lower(Goal.name) == data.name.lower())
    )

    if existing:
        logger.warning("goal_create_duplicate", user_id=current_user_id, name=data.name)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Накопление с таким именем уже существует")

    new_goal = Goal(user_id=current_user_id, name=data.name, target_amount=data.target_amount, deadline=data.deadline)

    db.add(new_goal)
    await db.commit()
    await db.refresh(new_goal)

    logger.info("goal_created", goal_id=new_goal.id, user_id=current_user_id)

    return GoalResponse(
            id=new_goal.id,
            name=new_goal.name,
            target_amount=new_goal.target_amount,
            current_amount=0,
            deadline=new_goal.deadline,
        )

async def add_money_to_goal_data(goal_id: int, data: ContributionCreate, current_user_id: int, db: AsyncSession):
    goal = await db.scalar(
        select(Goal)
        .where(Goal.id == goal_id, Goal.user_id == current_user_id)
    )

    if goal is None:
        logger.warning("goal_not_found", goal_id=goal_id, user_id=current_user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Накопление не найдено")

    current = await db.scalar(
        select(func.coalesce(func.sum(GoalContribution.amount), 0))
        .where(GoalContribution.goal_id == goal_id)
    )

    if current + data.amount > goal.target_amount:
        logger.warning("contribution_exceeds_target", goal_id=goal_id, user_id=current_user_id, amount=str(data.amount))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Сумма превышает остаток до цели",
        )

    available = await get_available_data(current_user_id, db)

    if data.amount > available:
        logger.warning("contribution_insufficient_funds", goal_id=goal_id, user_id=current_user_id, amount=str(data.amount))
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Недостаточно свободных средст")

    new_contribution = GoalContribution(
        goal_id=goal_id,
        amount=data.amount,
    )

    db.add(new_contribution)
    await db.commit()

    logger.info("contribution_added", goal_id=goal_id, user_id=current_user_id, amount=str(data.amount))


async def delete_goal_data(goal_id: int, current_user_id: int, db: AsyncSession):
    goal = await db.scalar(
        select(Goal).where(Goal.id == goal_id, Goal.user_id == current_user_id)
    )

    if goal is None:
        logger.warning("goal_not_found", goal_id=goal_id, user_id=current_user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Накопление не найдено")
    
    await db.delete(goal)
    await db.commit()

    logger.info("goal_deleted", goal_id=goal_id, user_id=current_user_id)