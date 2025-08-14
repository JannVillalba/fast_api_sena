from fastapi import FastAPI
from app.routers import users, categories, tasks, stats

app = FastAPI(title="Sistema de Gestión de Tareas", version="1.0.0")

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
app.include_router(stats.router, prefix="/stats", tags=["Statistics"])

@app.get("/")
def root():
    return {"message": "API de Gestión de Tareas lista 🚀"}

# Endpoint 1: Hello World (OBLIGATORIO)
@app.get("/")
def hello_world():
    return {"message": "¡Mi primera API FastAPI!"}

# Endpoint 2: Info básica (OBLIGATORIO)
@app.get("/info")
def info():
    return {"api": "FastAPI", "week": 1, "status": "running"}