from fastapi import APIRouter, Query
from typing import Optional
from datetime import date
from app.database import fake_db

router = APIRouter()

@router.get("/overview")
def tasks_overview():
    """
    Estadísticas generales de todas las tareas.
    """
    total = len(fake_db.tasks_db)
    by_status = {}
    by_priority = {}

    for t in fake_db.tasks_db:
        by_status[t.status] = by_status.get(t.status, 0) + 1
        by_priority[t.priority] = by_priority.get(t.priority, 0) + 1

    return {
        "total_tasks": total,
        "tasks_by_status": by_status,
        "tasks_by_priority": by_priority
    }


@router.get("/productivity")
def productivity_report(user_id: Optional[int] = Query(None, description="Filtrar por usuario")):
    """
    Reporte de productividad global o por usuario.
    """
    tasks = fake_db.tasks_db
    if user_id:
        tasks = [t for t in tasks if t.user_id == user_id]

    completed = [t for t in tasks if t.status == "completed"]
    overdue = [
        t for t in tasks
        if t.due_date and t.due_date < date.today() and t.status != "completed"
    ]

    return {
        "total_tasks": len(tasks),
        "completed_tasks": len(completed),
        "overdue_tasks": len(overdue),
        "completion_rate": round(len(completed) / len(tasks) * 100, 2) if tasks else 0
    }
