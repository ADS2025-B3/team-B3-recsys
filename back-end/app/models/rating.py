from typing import Optional
from datetime import datetime
from sqlmodel import Field
from .base import SQLModel

class RatingBase(SQLModel):
    movie_id: int = Field(index=True, foreign_key="movie.id")
    rating: int = Field(ge=1, le=5)
    timestamp: Optional[int] = None


class Rating(RatingBase, table=True):
    """
    Stores a single rating for a movie.
    """

    id: Optional[int] = Field(default=None, primary_key=True)

    # Link to your User table. If this conflicts with MovieLens synthetic users,
    # you can temporarily remove `foreign_key="user.id"`.
    user_id: int = Field(index=True, foreign_key="user.id")
    #user_id: int = Field(index=True)
        
    # For ratings created inside your app (useful even if timestamp is None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    


class RatingCreate(RatingBase):
    """
    Schema for creating a rating via API.

    We *do not* expose user_id here, it will come from the authenticated user.
    """
    pass


class RatingRead(SQLModel):
    """
    Schema returned by the API when reading ratings.
    """
    id: int
    user_id: int
    movie_id: int
    rating: int
    timestamp: Optional[int] = None
    created_at: datetime
