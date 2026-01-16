"""
Task Service

Business logic for task management operations.
"""
from datetime import datetime
from typing import List, Optional

from src.models.task import Task, TaskCreate, TaskUpdate, Priority, TaskStatus
from src.services.database import get_db


class TaskService:
    """
    Service class for task-related operations.

    Handles all business logic for creating, reading, updating,
    and deleting tasks.
    """

    async def get_task(self, task_id: int) -> Optional[Task]:
        """
        Retrieve a single task by ID.

        Args:
            task_id: The unique identifier of the task.

        Returns:
            The task if found, None otherwise.
        """
        db = await get_db()
        return await db.tasks.find_one({"id": task_id})

    async def get_user_tasks(
        self,
        user_id: int,
        status: Optional[TaskStatus] = None,
        priority: Optional[Priority] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Task]:
        """
        Get all tasks for a specific user.

        Args:
            user_id: The user's ID.
            status: Optional status filter.
            priority: Optional priority filter.
            skip: Number of records to skip (pagination).
            limit: Maximum number of records to return.

        Returns:
            List of tasks matching the criteria.
        """
        db = await get_db()

        query = {"user_id": user_id}
        if status:
            query["status"] = status
        if priority:
            query["priority"] = priority

        cursor = db.tasks.find(query).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    async def create_task(
        self,
        task_data: TaskCreate,
        user_id: int
    ) -> Task:
        """
        Create a new task.

        Args:
            task_data: The task data from the request.
            user_id: The ID of the user creating the task.

        Returns:
            The created task with generated ID and timestamps.
        """
        db = await get_db()

        now = datetime.utcnow()
        task = Task(
            id=await self._get_next_id(db),
            **task_data.model_dump(),
            user_id=user_id,
            status=TaskStatus.PENDING,
            created_at=now,
            updated_at=now,
        )

        await db.tasks.insert_one(task.model_dump())
        return task

    async def update_task(
        self,
        task_id: int,
        task_data: TaskUpdate
    ) -> Optional[Task]:
        """
        Update an existing task.

        Args:
            task_id: The ID of the task to update.
            task_data: The fields to update.

        Returns:
            The updated task, or None if not found.
        """
        db = await get_db()

        update_data = task_data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()

        result = await db.tasks.find_one_and_update(
            {"id": task_id},
            {"$set": update_data},
            return_document=True
        )

        return Task(**result) if result else None

    async def delete_task(self, task_id: int) -> bool:
        """
        Delete a task.

        Args:
            task_id: The ID of the task to delete.

        Returns:
            True if deleted, False if not found.
        """
        db = await get_db()
        result = await db.tasks.delete_one({"id": task_id})
        return result.deleted_count > 0

    async def get_overdue_tasks(self, user_id: int) -> List[Task]:
        """
        Get all overdue tasks for a user.

        Returns tasks that have a due date in the past and are not completed.
        """
        db = await get_db()

        query = {
            "user_id": user_id,
            "status": {"$ne": TaskStatus.COMPLETED},
            "due_date": {"$lt": datetime.utcnow()}
        }

        cursor = db.tasks.find(query)
        return await cursor.to_list(length=100)

    async def _get_next_id(self, db) -> int:
        """Generate the next auto-increment ID for tasks."""
        result = await db.counters.find_one_and_update(
            {"_id": "tasks"},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=True
        )
        return result["seq"]
