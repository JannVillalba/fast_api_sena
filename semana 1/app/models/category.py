from pydantic import BaseModel

class Category(BaseModel):
    id: int
    name: str
    description: str
    color: str
    user_id: int

class CategoryCreate(BaseModel):
    name: str
    description: str
    color: str
    user_id: int
