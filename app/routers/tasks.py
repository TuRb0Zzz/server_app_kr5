from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List
from app.schemas import TaskCreate, TaskUpdateStatus, TaskResponse
from app.dependencies import get_current_user
from app.storage import get_storage, TaskStorage

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    current_user: int = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
):
    task_dict = task_data.model_dump()
    task_dict["owner_id"] = current_user
    created = storage.create(task_dict)
    return created

@router.get("/", response_model=List[TaskResponse])
def get_user_tasks(
    status: Optional[str] = Query(None, description="Filter by status (todo, in_progress, done)"),
    min_priority: Optional[int] = Query(None, ge=1, le=5, description="Minimum priority"),
    current_user: int = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
):
    tasks = storage.get_all_by_owner(current_user, status, min_priority)
    return tasks

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    current_user: int = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
):
    task = storage.get(task_id)
    if not task or task["owner_id"] != current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task

@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: int,
    update: TaskUpdateStatus,
    current_user: int = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
):
    task = storage.get(task_id)
    if not task or task["owner_id"] != current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    updated = storage.update_status(task_id, update.status.value)
    return updated

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: int = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
):
    task = storage.get(task_id)
    if not task or task["owner_id"] != current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    storage.delete(task_id)