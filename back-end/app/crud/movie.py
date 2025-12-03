from typing import List, Optional
from sqlmodel import Session, select
from app.models.movie import Movie

class MovieCRUD:
    def get(self, session: Session, movie_id: int) -> Optional[Movie]:
        return session.get(Movie, movie_id)

    def list(
        self,
        session: Session,
        limit: int = 50,
        offset: int = 0,
        genre: Optional[str] = None,
        q: Optional[str] = None
    ) -> List[Movie]:
        statement = select(Movie)

        if genre:
            statement = statement.where(Movie.genres.contains(genre))

        if q:
            statement = statement.where(Movie.title.ilike(f"%{q}%"))

        statement = statement.limit(limit).offset(offset)
        return session.exec(statement).all()

    def search(
        self, session: Session, query: str, limit: int = 50
    ) -> List[Movie]:
        statement = (
            select(Movie)
            .where(Movie.title.ilike(f"%{query}%"))
            .limit(limit)
        )
        return session.exec(statement).all()

    def list_genres(self, session: Session) -> List[str]:
        rows = session.exec(select(Movie.genres)).all()
        unique = set()
        for g in rows:
            for tag in g.split("|"):
                unique.add(tag)
        return sorted(list(unique))


movie_crud = MovieCRUD()
