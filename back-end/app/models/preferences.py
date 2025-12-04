from typing import Optional, List
from datetime import datetime
from sqlmodel import Field
from .base import SQLModel


# -------------------------------------------
# Base schema (used for create/update)
# -------------------------------------------
class UserPreferenceBase(SQLModel):
    preferred_genres: List[str]


# -------------------------------------------
# DATABASE MODEL (table=True)
# -------------------------------------------
class UserPreference(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="user.id")

    # Store genres *as string* in DB: "Action|Comedy|Drama"
    preferred_genres: Optional[str] = None

    updated_at: datetime = Field(default_factory=datetime.utcnow)


# -------------------------------------------
# CREATE schema
# -------------------------------------------
class UserPreferenceCreate(UserPreferenceBase):
    pass


# -------------------------------------------
# READ schema
# -------------------------------------------
class UserPreferenceRead(SQLModel):
    id: int
    preferred_genres: List[str]
    updated_at: Optional[datetime]

