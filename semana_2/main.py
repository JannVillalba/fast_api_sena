from fastapi import FastAPI, HTTPException, Query, Path, status
from typing import Optional, List
import asyncio
from datetime import datetime, date
import uuid

# Importar modelos
from models import (
    UserCreate, UserResponse, UserUpdate,
    ProjectCreate, ProjectResponse, ProjectUpdate,
    TaskCreate, TaskResponse, TaskUpdate, TaskStatus, TaskPriority,
    CommentCreate, CommentResponse, CommentUpdate,
    UserType
)

app = FastAPI(
    title="Sistema de Gestión de Tareas",
    description="API para gestión de tareas, proyectos y usuarios",
    version="1.0.0"
)

# Almacenamiento en memoria (simulando base de datos)
users_db = {}
projects_db = {}
tasks_db = {}
comments_db = {}
user_counter = 1
project_counter = 1
task_counter = 1
comment_counter = 1

# Funciones de simulación async
async def validate_external_email(email: str) -> bool:
    """Simula validación externa de email"""
    await asyncio.sleep(0.5)  # Simular latencia API externa
    return "@" in email and "." in email

async def send_notification(user_id: int, message: str) -> bool:
    """Simula envío de notificación"""
    await asyncio.sleep(0.3)  # Simular envío
    print(f"Notificación enviada al usuario {user_id}: {message}")
    return True

async def backup_project(project_id: int) -> dict:
    """Simula backup de proyecto"""
    await asyncio.sleep(1)  # Simular proceso de backup
    backup_id = f"bk_{project_id}_{datetime.now().timestamp()}"
    print(f"Backup realizado: {backup_id}")
    return {"backup_id": backup_id}

# Endpoints para Users
@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    global user_counter
    
    # Validar email externamente
    email_valid = await validate_external_email(user.email)
    if not email_valid:
        raise HTTPException(status_code=400, detail="Email inválido")
    
    # Verificar si el email ya existe
    for existing_user in users_db.values():
        if existing_user["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email ya registrado")
    
    # Crear usuario
    user_id = user_counter
    user_counter += 1
    
    now = datetime.now()
    user_data = {
        "id": user_id,
        "name": user.name,
        "email": user.email,
        "type": user.type,
        "active": user.active,
        "password": user.password,  # En producción, esto debería ser hash
        "registration_date": now,
        "last_access": None
    }
    
    users_db[user_id] = user_data
    
    # Enviar notificación en segundo plano
    asyncio.create_task(send_notification(user_id, "Bienvenido al sistema de gestión de tareas"))
    
    return user_data

@app.get("/users", response_model=List[UserResponse])
async def list_users(
    active: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    type: Optional[UserType] = Query(None, description="Filtrar por tipo de usuario"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    filtered_users = list(users_db.values())
    
    if active is not None:
        filtered_users = [u for u in filtered_users if u["active"] == active]
    
    if type is not None:
        filtered_users = [u for u in filtered_users if u["type"] == type]
    
    # Paginación
    start_idx = (page - 1) * size
    end_idx = start_idx + size
    paginated_users = filtered_users[start_idx:end_idx]
    
    return paginated_users

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int = Path(..., ge=1)):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return users_db[user_id]

@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserCreate):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar si el email ya existe en otro usuario
    for uid, existing_user in users_db.items():
        if uid != user_id and existing_user["email"] == user_update.email:
            raise HTTPException(status_code=400, detail="Email ya registrado")
    
    # Actualizar usuario
    users_db[user_id].update({
        "name": user_update.name,
        "email": user_update.email,
        "type": user_update.type,
        "active": user_update.active,
        "password": user_update.password
    })
    
    return users_db[user_id]

@app.patch("/users/{user_id}", response_model=UserResponse)
async def partial_update_user(user_id: int, user_update: UserUpdate):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    update_data = user_update.dict(exclude_unset=True)
    
    # Si se actualiza el email, verificar que no exista en otro usuario
    if "email" in update_data:
        for uid, existing_user in users_db.items():
            if uid != user_id and existing_user["email"] == update_data["email"]:
                raise HTTPException(status_code=400, detail="Email ya registrado")
    
    # Actualizar campos proporcionados
    for field, value in update_data.items():
        users_db[user_id][field] = value
    
    return users_db[user_id]

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Soft delete (marcar como inactivo)
    users_db[user_id]["active"] = False
    
    return {"message": "Usuario desactivado correctamente"}

@app.get("/users/search", response_model=List[UserResponse])
async def search_users(
    name: Optional[str] = Query(None, min_length=1, description="Buscar por nombre"),
    email: Optional[str] = Query(None, min_length=1, description="Buscar por email"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    filtered_users = list(users_db.values())
    
    if name:
        filtered_users = [u for u in filtered_users if name.lower() in u["name"].lower()]
    
    if email:
        filtered_users = [u for u in filtered_users if email.lower() in u["email"].lower()]
    
    # Paginación
    start_idx = (page - 1) * size
    end_idx = start_idx + size
    paginated_users = filtered_users[start_idx:end_idx]
    
    return paginated_users

@app.get("/users/{user_id}/tasks", response_model=List[TaskResponse])
async def get_user_tasks(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user_tasks = [task for task in tasks_db.values() if task["assigned_to"] == user_id]
    return user_tasks

@app.patch("/users/{user_id}/last-access")
async def update_last_access(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    users_db[user_id]["last_access"] = datetime.now()
    
    return {"message": "Último acceso actualizado"}

# Endpoints para Projects
@app.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project: ProjectCreate):
    global project_counter
    
    # Verificar que el manager existe
    if project.manager_id not in users_db:
        raise HTTPException(status_code=400, detail="El manager especificado no existe")
    
    project_id = project_counter
    project_counter += 1
    
    now = datetime.now()
    project_data = {
        "id": project_id,
        "name": project.name,
        "description": project.description,
        "start_date": project.start_date,
        "due_date": project.due_date,
        "manager_id": project.manager_id,
        "creation_date": now,
        "total_tasks": 0,
        "completed_tasks": 0
    }
    
    projects_db[project_id] = project_data
    return project_data

@app.get("/projects", response_model=List[ProjectResponse])
async def list_projects(
    manager_id: Optional[int] = Query(None, ge=1, description="Filtrar por manager"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    filtered_projects = list(projects_db.values())
    
    if manager_id is not None:
        filtered_projects = [p for p in filtered_projects if p["manager_id"] == manager_id]
    
    # Paginación
    start_idx = (page - 1) * size
    end_idx = start_idx + size
    paginated_projects = filtered_projects[start_idx:end_idx]
    
    return paginated_projects

@app.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int = Path(..., ge=1)):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    return projects_db[project_id]

@app.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: int, project_update: ProjectCreate):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    # Verificar que el manager existe
    if project_update.manager_id not in users_db:
        raise HTTPException(status_code=400, detail="El manager especificado no existe")
    
    # Actualizar proyecto
    projects_db[project_id].update({
        "name": project_update.name,
        "description": project_update.description,
        "start_date": project_update.start_date,
        "due_date": project_update.due_date,
        "manager_id": project_update.manager_id
    })
    
    return projects_db[project_id]

@app.delete("/projects/{project_id}")
async def delete_project(project_id: int):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    # Hacer backup antes de eliminar
    backup_result = await backup_project(project_id)
    
    # Eliminar proyecto
    del projects_db[project_id]
    
    # Eliminar tareas asociadas
    global tasks_db
    tasks_db = {tid: task for tid, task in tasks_db.items() if task["project_id"] != project_id}
    
    return {"message": "Proyecto eliminado", "backup_id": backup_result["backup_id"]}

@app.get("/projects/search", response_model=List[ProjectResponse])
async def search_projects(
    name: Optional[str] = Query(None, min_length=1, description="Buscar por nombre"),
    description: Optional[str] = Query(None, min_length=1, description="Buscar en descripción"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    filtered_projects = list(projects_db.values())
    
    if name:
        filtered_projects = [p for p in filtered_projects if name.lower() in p["name"].lower()]
    
    if description:
        filtered_projects = [p for p in filtered_projects if p["description"] and description.lower() in p["description"].lower()]
    
    # Paginación
    start_idx = (page - 1) * size
    end_idx = start_idx + size
    paginated_projects = filtered_projects[start_idx:end_idx]
    
    return paginated_projects

@app.get("/projects/{project_id}/tasks", response_model=List[TaskResponse])
async def get_project_tasks(project_id: int):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    project_tasks = [task for task in tasks_db.values() if task["project_id"] == project_id]
    return project_tasks

@app.get("/projects/{project_id}/statistics")
async def get_project_statistics(project_id: int):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    project_tasks = [task for task in tasks_db.values() if task["project_id"] == project_id]
    total_tasks = len(project_tasks)
    completed_tasks = len([task for task in project_tasks if task["status"] == TaskStatus.completed])
    
    # Actualizar estadísticas en el proyecto
    projects_db[project_id]["total_tasks"] = total_tasks
    projects_db[project_id]["completed_tasks"] = completed_tasks
    
    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "completion_percentage": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    }

# Endpoints para Tasks
@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate):
    global task_counter
    
    # Verificar que el proyecto existe
    if task.project_id not in projects_db:
        raise HTTPException(status_code=400, detail="El proyecto especificado no existe")
    
    # Verificar que el usuario asignado existe (si se especifica)
    if task.assigned_to and task.assigned_to not in users_db:
        raise HTTPException(status_code=400, detail="El usuario asignado no existe")
    
    task_id = task_counter
    task_counter += 1
    
    now = datetime.now()
    task_data = {
        "id": task_id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "due_date": task.due_date,
        "project_id": task.project_id,
        "assigned_to": task.assigned_to,
        "estimated_hours": task.estimated_hours,
        "creation_date": now,
        "update_date": now,
        "created_by": 1  # En un sistema real, esto vendría del usuario autenticado
    }
    
    tasks_db[task_id] = task_data
    
    # Actualizar estadísticas del proyecto
    await get_project_statistics(task.project_id)
    
    # Notificar al usuario asignado si existe
    if task.assigned_to:
        asyncio.create_task(send_notification(
            task.assigned_to, 
            f"Has sido asignado a la tarea: {task.title}"
        ))
    
    return task_data

@app.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filtrar por estado"),
    priority: Optional[TaskPriority] = Query(None, description="Filtrar por prioridad"),
    project_id: Optional[int] = Query(None, ge=1, description="Filtrar por proyecto"),
    assigned_to: Optional[int] = Query(None, ge=1, description="Filtrar por usuario asignado"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    filtered_tasks = list(tasks_db.values())
    
    if status is not None:
        filtered_tasks = [t for t in filtered_tasks if t["status"] == status]
    
    if priority is not None:
        filtered_tasks = [t for t in filtered_tasks if t["priority"] == priority]
    
    if project_id is not None:
        filtered_tasks = [t for t in filtered_tasks if t["project_id"] == project_id]
    
    if assigned_to is not None:
        filtered_tasks = [t for t in filtered_tasks if t["assigned_to"] == assigned_to]
    
    # Paginación
    start_idx = (page - 1) * size
    end_idx = start_idx + size
    paginated_tasks = filtered_tasks[start_idx:end_idx]
    
    return paginated_tasks

@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int = Path(..., ge=1)):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    return tasks_db[task_id]

@app.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_update: TaskCreate):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    # Verificar que el proyecto existe
    if task_update.project_id not in projects_db:
        raise HTTPException(status_code=400, detail="El proyecto especificado no existe")
    
    # Verificar que el usuario asignado existe (si se especifica)
    if task_update.assigned_to and task_update.assigned_to not in users_db:
        raise HTTPException(status_code=400, detail="El usuario asignado no existe")
    
    # Actualizar tarea
    tasks_db[task_id].update({
        "title": task_update.title,
        "description": task_update.description,
        "status": task_update.status,
        "priority": task_update.priority,
        "due_date": task_update.due_date,
        "project_id": task_update.project_id,
        "assigned_to": task_update.assigned_to,
        "estimated_hours": task_update.estimated_hours,
        "update_date": datetime.now()
    })
    
    # Actualizar estadísticas del proyecto
    await get_project_statistics(task_update.project_id)
    
    return tasks_db[task_id]

@app.patch("/tasks/{task_id}", response_model=TaskResponse)
async def partial_update_task(task_id: int, task_update: TaskUpdate):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    update_data = task_update.dict(exclude_unset=True)
    
    # Verificaciones para campos específicos
    if "project_id" in update_data and update_data["project_id"] not in projects_db:
        raise HTTPException(status_code=400, detail="El proyecto especificado no existe")
    
    if "assigned_to" in update_data and update_data["assigned_to"] not in users_db:
        raise HTTPException(status_code=400, detail="El usuario asignado no existe")
    
    # Actualizar campos proporcionados
    for field, value in update_data.items():
        tasks_db[task_id][field] = value
    
    # Siempre actualizar la fecha de modificación
    tasks_db[task_id]["update_date"] = datetime.now()
    
    # Actualizar estadísticas del proyecto si cambió el estado
    if "status" in update_data:
        await get_project_statistics(tasks_db[task_id]["project_id"])
    
    return tasks_db[task_id]

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    project_id = tasks_db[task_id]["project_id"]
    del tasks_db[task_id]
    
    # Actualizar estadísticas del proyecto
    await get_project_statistics(project_id)
    
    return {"message": "Tarea eliminada correctamente"}

@app.get("/tasks/search", response_model=List[TaskResponse])
async def search_tasks(
    title: Optional[str] = Query(None, min_length=1, description="Buscar por título"),
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    project_id: Optional[int] = Query(None, ge=1),
    assigned_to: Optional[int] = Query(None, ge=1),
    due_date_from: Optional[date] = None,
    due_date_to: Optional[date] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    order_by: str = Query("creation_date", regex="^(title|creation_date|due_date|priority)$"),
    order_dir: str = Query("desc", regex="^(asc|desc)$")
):
    filtered_tasks = list(tasks_db.values())
    
    if title:
        filtered_tasks = [t for t in filtered_tasks if title.lower() in t["title"].lower()]
    
    if status:
        filtered_tasks = [t for t in filtered_tasks if t["status"] == status]
    
    if priority:
        filtered_tasks = [t for t in filtered_tasks if t["priority"] == priority]
    
    if project_id:
        filtered_tasks = [t for t in filtered_tasks if t["project_id"] == project_id]
    
    if assigned_to:
        filtered_tasks = [t for t in filtered_tasks if t["assigned_to"] == assigned_to]
    
    if due_date_from:
        filtered_tasks = [t for t in filtered_tasks if t["due_date"] and t["due_date"] >= due_date_from]
    
    if due_date_to:
        filtered_tasks = [t for t in filtered_tasks if t["due_date"] and t["due_date"] <= due_date_to]
    
    # Ordenamiento
    reverse = order_dir == "desc"
    filtered_tasks.sort(key=lambda x: x.get(order_by, ""), reverse=reverse)
    
    # Paginación
    start_idx = (page - 1) * size
    end_idx = start_idx + size
    paginated_tasks = filtered_tasks[start_idx:end_idx]
    
    return paginated_tasks

@app.patch("/tasks/{task_id}/status")
async def change_task_status(task_id: int, new_status: TaskStatus):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    old_status = tasks_db[task_id]["status"]
    tasks_db[task_id]["status"] = new_status
    tasks_db[task_id]["update_date"] = datetime.now()
    
    # Actualizar estadísticas del proyecto
    await get_project_statistics(tasks_db[task_id]["project_id"])
    
    # Notificar al usuario asignado si existe
    if tasks_db[task_id]["assigned_to"]:
        asyncio.create_task(send_notification(
            tasks_db[task_id]["assigned_to"], 
            f"El estado de la tarea '{tasks_db[task_id]['title']}' ha cambiado de {old_status} a {new_status}"
        ))
    
    return {"message": "Estado actualizado correctamente"}

@app.patch("/tasks/{task_id}/assign")
async def assign_task(task_id: int, user_id: int):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    if user_id not in users_db:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")
    
    old_assignee = tasks_db[task_id]["assigned_to"]
    tasks_db[task_id]["assigned_to"] = user_id
    tasks_db[task_id]["update_date"] = datetime.now()
    
    # Notificar al nuevo usuario asignado
    asyncio.create_task(send_notification(
        user_id, 
        f"Has sido asignado a la tarea: {tasks_db[task_id]['title']}"
    ))
    
    # Notificar al anterior usuario asignado (si existía y es diferente)
    if old_assignee and old_assignee != user_id:
        asyncio.create_task(send_notification(
            old_assignee, 
            f"Has sido desasignado de la tarea: {tasks_db[task_id]['title']}"
        ))
    
    return {"message": "Tarea asignada correctamente"}

@app.get("/tasks/statistics")
async def get_tasks_statistics():
    total_tasks = len(tasks_db)
    completed_tasks = len([t for t in tasks_db.values() if t["status"] == TaskStatus.completed])
    in_progress_tasks = len([t for t in tasks_db.values() if t["status"] == TaskStatus.in_progress])
    pending_tasks = len([t for t in tasks_db.values() if t["status"] == TaskStatus.pending])
    
    # Tareas por prioridad
    priority_stats = {
        "low": len([t for t in tasks_db.values() if t["priority"] == TaskPriority.low]),
        "medium": len([t for t in tasks_db.values() if t["priority"] == TaskPriority.medium]),
        "high": len([t for t in tasks_db.values() if t["priority"] == TaskPriority.high]),
        "critical": len([t for t in tasks_db.values() if t["priority"] == TaskPriority.critical])
    }
    
    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "in_progress_tasks": in_progress_tasks,
        "pending_tasks": pending_tasks,
        "completion_percentage": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
        "priority_stats": priority_stats
    }

# Endpoints para Comments
@app.post("/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(comment: CommentCreate):
    global comment_counter
    
    # Verificar que la tarea existe
    if comment.task_id not in tasks_db:
        raise HTTPException(status_code=400, detail="La tarea especificada no existe")
    
    comment_id = comment_counter
    comment_counter += 1
    
    now = datetime.now()
    comment_data = {
        "id": comment_id,
        "content": comment.content,
        "task_id": comment.task_id,
        "creation_date": now,
        "author_id": 1,  # En un sistema real, esto vendría del usuario autenticado
        "author_name": "Admin"  # En un sistema real, esto vendría de la base de datos
    }
    
    comments_db[comment_id] = comment_data
    return comment_data

@app.get("/comments/task/{task_id}", response_model=List[CommentResponse])
async def get_task_comments(task_id: int):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    task_comments = [comment for comment in comments_db.values() if comment["task_id"] == task_id]
    return task_comments

@app.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(comment_id: int, comment_update: CommentCreate):
    if comment_id not in comments_db:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")
    
    # Verificar que la tarea existe
    if comment_update.task_id not in tasks_db:
        raise HTTPException(status_code=400, detail="La tarea especificada no existe")
    
    comments_db[comment_id].update({
        "content": comment_update.content,
        "task_id": comment_update.task_id
    })
    
    return comments_db[comment_id]

@app.delete("/comments/{comment_id}")
async def delete_comment(comment_id: int):
    if comment_id not in comments_db:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")
    
    del comments_db[comment_id]
    return {"message": "Comentario eliminado correctamente"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)