from fastapi import APIRouter, HTTPException
from typing import List

from app.models import RatingCreate, RatingRead
from app.crud.rating import rating_crud
from app.api.deps import (
    CurrentUser,
    SessionDep,
)
router = APIRouter()

@router.post("/", response_model=RatingRead)
def create_rating(
    rating_in: RatingCreate,
    session: SessionDep,
    current_user: CurrentUser
):
    # Check if user has rated before
    existing = rating_crud.get_user_rating(
        session=session,
        user_id=current_user.id,
        movie_id=rating_in.movie_id
    )
    
    print(existing)

    if existing:
        updated_rating = rating_crud.update(
            session=session,
            rating=existing,
            new_rating_value=rating_in.rating,
            new_timestamp=rating_in.timestamp
        )
        return updated_rating
    new_rating = rating_crud.create(
        session=session,
        user_id=current_user.id,
        movie_id=rating_in.movie_id,
        rating_value=rating_in.rating,
        timestamp=rating_in.timestamp
    )

    return new_rating


@router.get("/me", response_model=List[RatingRead])
def list_my_ratings(
    session: SessionDep,
    current_user: CurrentUser
):
    return rating_crud.list_user_ratings(session, current_user.id)

@router.get("/{movie_id}/me", response_model=RatingRead | None)
def get_my_rating_for_movie(
    movie_id: int,
    session: SessionDep,
    current_user: CurrentUser
):
    return rating_crud.get_user_rating(
        session=session,
        user_id=current_user.id,
        movie_id=movie_id
    )