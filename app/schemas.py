from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"

class TaskBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=80)
    description: Optional[str] = None
    status: TaskStatus
    priority: int = Field(..., ge=1, le=5)

class TaskCreate(TaskBase):
    pass

class TaskUpdateStatus(BaseModel):
    status: TaskStatus

class TaskResponse(TaskBase):
    id: int
    owner_id: int