from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime, date
from enum import Enum
from typing import Optional, List

class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"

class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class UserType(str, Enum):
    admin = "admin"
    manager = "manager"
    developer = "developer"
    viewer = "viewer"

# Modelo base para User
class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    type: UserType
    active: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Mínimo 8 caracteres")

class UserResponse(UserBase):
    id: int
    registration_date: datetime
    last_access: Optional[datetime] = None

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    type: Optional[UserType] = None
    active: Optional[bool] = None
    last_access: Optional[datetime] = None

# Modelo base para Project
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    start_date: date
    due_date: Optional[date] = None
    manager_id: int = Field(..., ge=1)

    @validator('due_date')
    def validate_due_date(cls, v, values):
        if v and values.get('start_date'):
            if v <= values['start_date']:
                raise ValueError('Due date must be after start date')
        return v

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    creation_date: datetime
    total_tasks: int = 0
    completed_tasks: int = 0

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    manager_id: Optional[int] = Field(None, ge=1)

# Modelo base para Task
class TaskBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: TaskStatus = TaskStatus.pending
    priority: TaskPriority = TaskPriority.medium
    due_date: Optional[date] = None
    project_id: int = Field(..., ge=1)
    assigned_to: Optional[int] = Field(None, ge=1)
    estimated_hours: Optional[float] = Field(None, ge=0.1, le=1000)

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int
    creation_date: datetime
    update_date: datetime
    created_by: int

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[date] = None
    assigned_to: Optional[int] = Field(None, ge=1)
    estimated_hours: Optional[float] = Field(None, ge=0.1, le=1000)

# Modelo para Comment
class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)
    task_id: int = Field(..., ge=1)

class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id: int
    creation_date: datetime
    author_id: int
    author_name: str

class CommentUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=1000)