from .deps import *

class Movie(SQLModel, table=True):
    id: int = Field(primary_key=True)
    title: str
    genres: str  # stored as "Adventure|Children|Fantasy"
    release_year: Optional[int] = None