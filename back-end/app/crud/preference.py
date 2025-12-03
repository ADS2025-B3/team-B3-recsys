from sqlmodel import Session, select
from typing import Optional
from app.models import UserPreference


class UserPreferenceCRUD:
    def get_by_user(self, session: Session, user_id: int) -> Optional[UserPreference]:
        statement = select(UserPreference).where(UserPreference.user_id == user_id)
        return session.exec(statement).first()


    def set_preferences(self, session: Session, user_id: int, genres: list[str]) -> UserPreference:
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


user_preference_crud = UserPreferenceCRUD()
