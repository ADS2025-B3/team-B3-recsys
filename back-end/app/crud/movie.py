from typing import List, Optional
from sqlmodel import Session, select, func
from app.models.movie import Movie
from app.models.rating import Rating

class MovieCRUD:
    def _add_rating_stats(self, session: Session, movie: Movie) -> dict:
        """Add rating statistics to a movie"""
        stats = session.exec(
            select(
                func.avg(Rating.rating).label('average_rating'),
                func.count(Rating.id).label('rating_count')
            ).where(Rating.movie_id == movie.id)
        ).first()
        
        return {
            **movie.model_dump(),
            'average_rating': float(stats[0]) if stats[0] is not None else None,
            'rating_count': stats[1] if stats[1] is not None else 0
        }

    def get(self, session: Session, movie_id: int) -> Optional[dict]:
        movie = session.get(Movie, movie_id)
        if not movie:
            return None
        return self._add_rating_stats(session, movie)

    def list(
        self,
        session: Session,
        limit: int = 50,
        offset: int = 0,
        genre: Optional[str] = None,
        q: Optional[str] = None
    ) -> List[dict]:
        statement = select(Movie)

        if genre:
            statement = statement.where(Movie.genres.contains(genre))

        if q:
            statement = statement.where(Movie.title.ilike(f"%{q}%"))

        statement = statement.limit(limit).offset(offset)
        movies = session.exec(statement).all()
        
        return [self._add_rating_stats(session, movie) for movie in movies]

    def search(
        self, session: Session, query: str, limit: int = 50
    ) -> List[dict]:
        statement = (
            select(Movie)
            .where(Movie.title.ilike(f"%{query}%"))
            .limit(limit)
        )
        movies = session.exec(statement).all()
        
        return [self._add_rating_stats(session, movie) for movie in movies]

    def list_genres(self, session: Session) -> List[str]:
        rows = session.exec(select(Movie.genres)).all()
        unique = set()
        for g in rows:
            for tag in g.split("|"):
                unique.add(tag)
        return sorted(list(unique))


movie_crud = MovieCRUD()
