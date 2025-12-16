from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class User(SQLModel, table=True):
    __tablename__ = "user"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    full_name: Optional[str] = None
    role: Optional[str] = None
    # Añade otros campos según tu esquema


class Rating(SQLModel, table=True):
    __tablename__ = "rating"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    movie_id: int
    rating: float
    created_at: Optional[datetime] = None
    # Añade otros campos según tu esquema