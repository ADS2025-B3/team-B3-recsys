from sqlmodel import Field
from .base import SQLModel
from typing import Optional

class Movie(SQLModel, table=True):
    id: int = Field(primary_key=True)
    title: str
    genres: str  # stored as "Adventure|Children|Fantasy"
    release_year: Optional[int] = None


class MovieRead(SQLModel):
    id: int
    title: str
    genres: str
    release_year: Optional[int]
    average_rating: Optional[float] = None
    rating_count: Optional[int] = None