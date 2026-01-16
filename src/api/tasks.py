"""
Tasks API Router

Provides CRUD endpoints for task management.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from src.models.task import Task, TaskCreate, TaskUpdate, TaskAssignment, Priority, TaskStatus
from src.models.user import User
from src.services.task_service import TaskService
from src.services.auth_service import AuthService, get_current_user

router = APIRouter()


@router.get("/", response_model=List[Task])
async def list_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[Priority] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
):
    """
    List all tasks for the current user.

    Supports filtering by status and priority, with pagination.
    """
    service = TaskService()
    return await service.get_user_tasks(
        user_id=current_user.id,
        status=status,
        priority=priority,
        skip=skip,
        limit=limit,
    )


@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific task by ID.

    Returns 404 if the task doesn't exist or doesn't belong to the user.
    """
    service = TaskService()
    task = await service.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")

    return task


@router.post("/", response_model=Task, status_code=201)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
):
    """
    Create a new task.

    The task will be assigned to the current user.
    """
    service = TaskService()
    return await service.create_task(task_data, user_id=current_user.id)


@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing task.

    Only the task owner or an admin can update a task.
    """
    service = TaskService()
    task = await service.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")

    return await service.update_task(task_id, task_data)


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
):
    """
    Delete a task.

    Only the task owner or an admin can delete a task.
    """
    service = TaskService()
    task = await service.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")

    await service.delete_task(task_id)


@router.post("/{task_id}/complete", response_model=Task)
async def complete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
):
    """
    Mark a task as completed.

    Shortcut endpoint to quickly complete a task.
    """
    service = TaskService()
    task = await service.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return await service.update_task(
        task_id,
        TaskUpdate(status=TaskStatus.COMPLETED)
    )


@router.post("/{task_id}/assign", response_model=Task)
async def assign_task(
    task_id: int,
    assignment: TaskAssignment,
    current_user: User = Depends(get_current_user),
):
    """
    Assign a task to another user.

    Only the task owner or an admin can assign tasks.
    The target user must exist in the system.
    """
    task_service = TaskService()
    auth_service = AuthService()

    # Get the task
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check permissions
    if task.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")

    # Verify target user exists
    target_user = await auth_service.get_user_by_id(assignment.assigned_to)
    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found")

    # Update the task assignment
    return await task_service.update_task(
        task_id,
        TaskUpdate(assigned_to=assignment.assigned_to)
    )
