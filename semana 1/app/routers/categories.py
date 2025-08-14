from fastapi import APIRouter, HTTPException
from app.models.category import Category, CategoryCreate
from app.database import fake_db

router = APIRouter()

@router.post("/", response_model=Category)
def create_category(category: CategoryCreate):
    new_category = Category(
        id=fake_db.category_id_counter,
        name=category.name,
        description=category.description,
        color=category.color,
        user_id=category.user_id
    )
    fake_db.categories_db.append(new_category)
    fake_db.category_id_counter += 1
    return new_category

@router.get("/", response_model=list[Category])
def list_categories():
    return fake_db.categories_db

@router.put("/{category_id}", response_model=Category)
def update_category(category_id: int, category: CategoryCreate):
    for idx, c in enumerate(fake_db.categories_db):
        if c.id == category_id:
            updated_category = Category(id=category_id, **category.dict())
            fake_db.categories_db[idx] = updated_category
            return updated_category
    raise HTTPException(status_code=404, detail="Category not found")

@router.delete("/{category_id}")
def delete_category(category_id: int):
    for idx, c in enumerate(fake_db.categories_db):
        if c.id == category_id:
            del fake_db.categories_db[idx]
            return {"message": "Category deleted"}
    raise HTTPException(status_code=404, detail="Category not found")
