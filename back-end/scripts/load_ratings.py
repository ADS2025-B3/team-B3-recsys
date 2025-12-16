import pandas as pd
from sqlmodel import Session
from app.core.db import engine

def main():
    
    CSV_PATH = "../data/processed/train.csv"

    df = pd.read_csv(CSV_PATH)

    USER_ID =2

    userRatingPerMovie = df[df['user_id'] == USER_ID][['item_id', 'rating']]

    with Session(engine) as session:
        for _, row in userRatingPerMovie.iterrows():
            movie_id = int(row["item_id"])
            rating_value = int(row["rating"])
            timestamp = None  # or set to a specific value if available
            # Check if the rating already exists
            from app.crud.rating import rating_crud
            # Create new rating
            rating_crud.create(
                session,
                user_id=USER_ID,
                movie_id=movie_id,
                rating_value=rating_value,
                timestamp=timestamp
            )
        session.commit()

if __name__ == "__main__":
    main()

    # to run this file_
    # cd backend
    # python3 -m scripts.load_ratings