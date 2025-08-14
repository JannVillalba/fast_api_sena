from fastapi import APIRouter, HTTPException
from app.models.user import User, UserCreate
from app.database import fake_db
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=User)
def create_user(user: UserCreate):
    global fake_db
    new_user = User(
        id=fake_db.user_id_counter,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        created_at=datetime.now(),
        preferences=user.preferences
    )
    fake_db.users_db.append(new_user)
    fake_db.user_id_counter += 1
    return new_user

@router.get("/{user_id}", response_model=User)
def get_user(user_id: int):
    for u in fake_db.users_db:
        if u.id == user_id:
            return u
    raise HTTPException(status_code=404, detail="User not found")

@router.put("/{user_id}", response_model=User)
def update_user(user_id: int, user: UserCreate):
    for idx, u in enumerate(fake_db.users_db):
        if u.id == user_id:
            updated_user = User(
                id=user_id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                created_at=u.created_at,
                preferences=user.preferences
            )
            fake_db.users_db[idx] = updated_user
            return updated_user
    raise HTTPException(status_code=404, detail="User not found")

@router.delete("/{user_id}")
def delete_user(user_id: int):
    for idx, u in enumerate(fake_db.users_db):
        if u.id == user_id:
            del fake_db.users_db[idx]
            return {"message": "User deleted"}
    raise HTTPException(status_code=404, detail="User not found")
