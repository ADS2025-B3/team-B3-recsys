from sqlmodel import Session, select
from typing import Optional, List
from fastapi import HTTPException

from app.models import UserPreference
from app.core.constants import MOVIE_GENRES


class UserPreferenceCRUD:

    def validate_genres(self, genres: List[str]):
        invalid = [g for g in genres if g not in MOVIE_GENRES]
        if invalid:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid genres: {invalid}. Allowed genres: {MOVIE_GENRES}"
            )

    def get_by_user(self, session: Session, user_id: int) -> Optional[UserPreference]:
        statement = select(UserPreference).where(UserPreference.user_id == user_id)
        return session.exec(statement).first()

    def set_preferences(self, session: Session, user_id: int, genres: List[str]) -> UserPreference:

        # Validate input genres
        self.validate_genres(genres)

        genres_str = "|".join(genres)
        existing = self.get_by_user(session, user_id)

        if existing:
            existing.preferred_genres = genres_str
            session.add(existing)
            session.commit()
            session.refresh(existing)
            return existing

        pref = UserPreference(
            user_id=user_id,
            preferred_genres=genres_str
        )
        session.add(pref)
        session.commit()
        session.refresh(pref)
        return pref

    def update_preferences(self, session: Session, user_id: int, genres: List[str]) -> Optional[UserPreference]:

        # Validate input genres
        self.validate_genres(genres)

        existing = self.get_by_user(session, user_id)
        if not existing:
            return None

        existing.preferred_genres = "|".join(genres)
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing


user_preference_crud = UserPreferenceCRUD()