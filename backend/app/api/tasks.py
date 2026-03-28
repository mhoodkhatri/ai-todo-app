from datetime import datetime, timezone
from uuid import UUID

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.security import get_current_user
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    body: TaskCreate,
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Task:
    task = Task(
        user_id=user_id,
        title=body.title,
        description=body.description,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    status: Literal["all", "completed", "incomplete"] = Query(default="all"),
) -> list[Task]:
    query = select(Task).where(Task.user_id == user_id)
    if status == "completed":
        query = query.where(Task.is_completed == True)  # noqa: E712
    elif status == "incomplete":
        query = query.where(Task.is_completed == False)  # noqa: E712
    result = await session.exec(
        query.order_by(Task.created_at.desc())  # type: ignore[union-attr]
    )
    return list(result.all())


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Task:
    result = await session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    task = result.first()
    if not task:
        raise HTTPException(status_code=404, detail="Not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    body: TaskUpdate,
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Task:
    result = await session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    task = result.first()
    if not task:
        raise HTTPException(status_code=404, detail="Not found")
    task.title = body.title
    task.description = body.description
    task.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


@router.patch("/{task_id}/toggle", response_model=TaskResponse)
async def toggle_task(
    task_id: UUID,
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Task:
    result = await session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    task = result.first()
    if not task:
        raise HTTPException(status_code=404, detail="Not found")
    task.is_completed = not task.is_completed
    task.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: UUID,
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    result = await session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    task = result.first()
    if not task:
        raise HTTPException(status_code=404, detail="Not found")
    await session.delete(task)
    await session.commit()
