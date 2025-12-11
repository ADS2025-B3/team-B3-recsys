import pandas as pd
from sqlmodel import Session
from app.core.db import engine
from app.models.movie import Movie

CSV_PATH = "../data/processed/movielens/movies.csv"

def main():
    df = pd.read_csv(CSV_PATH)

    with Session(engine) as session:
        for _, row in df.iterrows():
            movie = Movie(
                id=int(row["movie_id"]),
                title=row["title"],
                genres=row["genres"],
                release_year=int(row["release_year"]) if not pd.isna(row["release_year"]) else None
            )
            session.merge(movie)  # avoids duplicates
        session.commit()

if __name__ == "__main__":
    main()

    # to run this file_
    # cd backend
    # python3 -m scripts.load_movies