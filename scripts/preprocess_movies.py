import pandas as pd
from pathlib import Path

RAW_PATH = Path("data/raw/ml-100k/u.item")
OUTPUT_PATH = Path("data/processed/movielens/movies.csv")

GENRE_COLUMNS = [
    "unknown", "Action", "Adventure", "Animation", "Children",
    "Comedy", "Crime", "Documentary", "Drama", "Fantasy",
    "Film-Noir", "Horror", "Musical", "Mystery", "Romance",
    "Sci-Fi", "Thriller", "War", "Western"
]

def main():
    df = pd.read_csv(
        RAW_PATH,
        sep="|",
        header=None,
        encoding="latin-1",
        names=[
            "movie_id", "title", "release_date", "video_release_date",
            "imdb_url", *GENRE_COLUMNS
        ],
    )

    # Extract genres
    df["genres"] = df[GENRE_COLUMNS].apply(
        lambda row: "|".join([genre for genre, val in row.items() if val == 1]),
        axis=1
    )

    # Extract release year
    df["release_year"] = df["release_date"].str[-4:].astype("Int64", errors="ignore")

    # Keep only required fields
    df = df[["movie_id", "title", "genres", "release_year"]]

    # Save processed file
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Processed movies saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
