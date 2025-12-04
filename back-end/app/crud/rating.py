from typing import Optional, List
from sqlmodel import Session, select
from app.models.rating import Rating


class RatingCRUD:
    def create(
        self, 
        session: Session, 
        user_id: int, 
        movie_id: int, 
        rating_value: int,
        timestamp: Optional[int] = None
    ) -> Rating:
        rating = Rating(
            user_id=user_id,
            movie_id=movie_id,
            rating=rating_value,
            timestamp=timestamp
        )
        session.add(rating)
        session.commit()
        session.refresh(rating)
        return rating

    def update(
        self,
        session: Session,
        rating: Rating,
        new_rating_value: int,
        new_timestamp: Optional[int] = None
    ) -> Rating:
        rating.rating = new_rating_value
        if new_timestamp is not None:
            rating.timestamp = new_timestamp
        session.add(rating)
        session.commit()
        session.refresh(rating)
        return rating
    def get_user_rating(
        self,
        session: Session,
        user_id: int,
        movie_id: int
    ) -> Optional[Rating]:
        statement = select(Rating).where(
            Rating.user_id == user_id,
            Rating.movie_id == movie_id
        )
        return session.exec(statement).first()

    def list_user_ratings(
        self,
        session: Session,
        user_id: int
    ) -> List[Rating]:
        statement = select(Rating).where(Rating.user_id == user_id)
        return session.exec(statement).all()


rating_crud = RatingCRUD()
