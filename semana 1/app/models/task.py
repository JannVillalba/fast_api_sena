from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Literal, Optional

PriorityType = Literal["low", "medium", "high", "urgent"]
StatusType = Literal["pending", "in_progress", "completed", "cancelled"]

class Task(BaseModel):
    id: int
    title: str
    description: str
    priority: PriorityType
    status: StatusType
    category_id: int
    user_id: int
    due_date: date
    created_at: datetime
    updated_at: datetime
    tags: List[str]

class TaskCreate(BaseModel):
    title: str
    description: str
    priority: PriorityType
    status: StatusType
    category_id: int
    user_id: int
    due_date: date
    tags: Optional[List[str]] = []
