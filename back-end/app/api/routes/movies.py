from fastapi import APIRouter, HTTPException
from typing import Optional, List

from app.api.deps import SessionDep
from app import crud
from app.models import MovieRead

router = APIRouter()

@router.get("/", response_model=List[MovieRead])
def list_movies(
    *,
    session: SessionDep,
    genre: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
):
    return crud.movie.movie_crud.list(
        session=session, genre=genre, q=q, limit=limit, offset=offset
    )


@router.get("/search", response_model=List[MovieRead])
def search_movies(session: SessionDep, q: str, limit: int = 50):
    return crud.movie.movie_crud.search(session, query=q, limit=limit)


@router.get("/{movie_id}", response_model=MovieRead)
def get_movie(session: SessionDep, movie_id: int):
    movie = crud.movie.movie_crud.get(session, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.get("/genres/", response_model=list[str])
def list_genres(session: SessionDep):
    return crud.movie.movie_crud.list_genres(session)