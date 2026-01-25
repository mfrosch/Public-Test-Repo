"""
Task Comments API

Provides endpoints for managing comments on tasks.
Users can add, view, and delete comments on their tasks.
"""
from typing import List
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class CommentCreate(BaseModel):
    """Request model for creating a new comment."""
    task_id: str
    text: str


class Comment(BaseModel):
    """Response model representing a task comment."""
    id: str
    task_id: str
    user_id: str
    text: str
    created_at: datetime


# In-memory storage for comments
_comments: dict[str, Comment] = {}
_counter = 0


@router.post("/", response_model=Comment, status_code=201)
async def create_comment(comment: CommentCreate, user_id: str = "demo_user"):
    """
    Create a new comment on a task.

    Adds a comment to the specified task. The comment will be
    associated with the current user and timestamped.

    Args:
        comment: The comment data containing task_id and text
        user_id: The ID of the user creating the comment

    Returns:
        The created comment with generated ID and timestamp
    """
    global _counter
    _counter += 1
    new_comment = Comment(
        id=f"comment_{_counter}",
        task_id=comment.task_id,
        user_id=user_id,
        text=comment.text,
        created_at=datetime.utcnow()
    )
    _comments[new_comment.id] = new_comment
    return new_comment


@router.get("/task/{task_id}", response_model=List[Comment])
async def get_task_comments(task_id: str):
    """
    Get all comments for a specific task.

    Retrieves all comments associated with the given task ID,
    ordered by creation time.

    Args:
        task_id: The ID of the task to get comments for

    Returns:
        List of comments for the specified task
    """
    return [c for c in _comments.values() if c.task_id == task_id]


@router.delete("/{comment_id}")
async def delete_comment(comment_id: str):
    """
    Delete a comment.

    Permanently removes a comment from the system.

    Args:
        comment_id: The ID of the comment to delete

    Returns:
        Confirmation that the comment was deleted

    Raises:
        HTTPException: 404 if comment not found
    """
    if comment_id not in _comments:
        raise HTTPException(status_code=404, detail="Comment not found")
    del _comments[comment_id]
    return {"deleted": True}
