from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.models.task import Task, TaskCreate
from app.database import fake_db
from datetime import datetime, date

router = APIRouter()

@router.post("/", response_model=Task)
def create_task(task: TaskCreate):
    new_task = Task(
        id=fake_db.task_id_counter,
        title=task.title,
        description=task.description,
        priority=task.priority,
        status=task.status,
        category_id=task.category_id,
        user_id=task.user_id,
        due_date=task.due_date,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        tags=task.tags
    )
    fake_db.tasks_db.append(new_task)
    fake_db.task_id_counter += 1
    return new_task


@router.get("/", response_model=list[Task])
def list_tasks(
    status: Optional[str] = Query(None, description="Filtro por estado"),
    priority: Optional[str] = Query(None, description="Filtro por prioridad"),
    user_id: Optional[int] = Query(None, description="Filtro por usuario"),
    category_id: Optional[int] = Query(None, description="Filtro por categoría"),
    due_before: Optional[date] = Query(None, description="Tareas con fecha límite antes de..."),
    due_after: Optional[date] = Query(None, description="Tareas con fecha límite después de...")
):
    results = fake_db.tasks_db

    if status:
        results = [t for t in results if t.status == status]
    if priority:
        results = [t for t in results if t.priority == priority]
    if user_id:
        results = [t for t in results if t.user_id == user_id]
    if category_id:
        results = [t for t in results if t.category_id == category_id]
    if due_before:
        results = [t for t in results if t.due_date and t.due_date < due_before]
    if due_after:
        results = [t for t in results if t.due_date and t.due_date > due_after]

    return results


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: int):
    for t in fake_db.tasks_db:
        if t.id == task_id:
            return t
    raise HTTPException(status_code=404, detail="Task not found")


@router.put("/{task_id}", response_model=Task)
def update_task(task_id: int, task: TaskCreate):
    for idx, t in enumerate(fake_db.tasks_db):
        if t.id == task_id:
            updated_task = Task(
                id=task_id,
                created_at=t.created_at,
                updated_at=datetime.now(),
                **task.dict()
            )
            fake_db.tasks_db[idx] = updated_task
            return updated_task
    raise HTTPException(status_code=404, detail="Task not found")


@router.delete("/{task_id}")
def delete_task(task_id: int):
    for idx, t in enumerate(fake_db.tasks_db):
        if t.id == task_id:
            del fake_db.tasks_db[idx]
            return {"message": "Task deleted"}
    raise HTTPException(status_code=404, detail="Task not found")