from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import User
from app.modules.goals.service import add_money_to_goal_data, create_goal_data, delete_goal_data, get_available_data, get_goals_data
from app.modules.goals.schemas import ContributionCreate, GoalCreate, GoalResponse
from app.api.deps import get_current_user, verify_csrf
from app.core.database import get_db


router = APIRouter()

@router.get("", response_model=list[GoalResponse])
async def get_goals(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_goals_data(current_user.id, db)

@router.post(
    "",
    response_model=GoalResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_csrf)],
)
async def create_goal(data: GoalCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await create_goal_data(data, current_user.id, db)

@router.post(
    "/{goal_id}/contributions",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_csrf)],
)
async def add_money_to_goal(goal_id: int, data: ContributionCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await add_money_to_goal_data(goal_id, data, current_user.id, db)

@router.get("/available", response_model=float)
async def get_available(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_available_data(current_user.id, db)

@router.delete(
    "/{goal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_csrf)],
)
async def delete_goal(goal_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await delete_goal_data(goal_id, current_user.id, db)