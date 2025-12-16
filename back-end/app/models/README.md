# HybridRecommender - Usage Guide

## Overview

The `HybridRecommender` is a sophisticated recommendation system that combines:

- **SVD Collaborative Filtering** - For users with existing ratings in the training data
- **Content-Based Filtering** - For new users based on movie genres
- **Hybrid Approach** - Combines user ratings with explicit genre preferences

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  User Profile                                           │
│  ├─ Historical Ratings (70% weight)                     │
│  └─ Preferred Genres (30% weight)                       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Recommendation Engine                                  │
│  ├─ Existing User → SVD Model                           │
│  └─ New User → Content-Based + Genre Similarity         │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Output                                                 │
│  ├─ Top-N Recommendations                               │
│  ├─ Rating Predictions (1-5 scale)                      │
│  ├─ Like/Dislike Classification                         │
│  └─ Explanations                                        │
└─────────────────────────────────────────────────────────┘
```

## Installation & Setup

### 1. Prerequisites

```bash
# Required packages
pip install numpy pandas scikit-learn scipy
```

### 2. Model Files Required

- **SVD Model**: Trained SVD collaborative filtering model (from MLflow or pickle)
- **Movies Catalog**: CSV file with columns: `movie_id`, `unknown`, `Action`, `Adventure`, ..., `Western`

### 3. Initialize the Recommender

```python
from app.models.HybridRecommender import HybridRecommender
import mlflow

# Option 1: Load from MLflow
svd_model = mlflow.sklearn.load_model("models:/MovieRatingPredictModel/Production")

# Option 2: Load from pickle
import pickle
with open('models/svd_model.pkl', 'rb') as f:
    svd_model = pickle.load(f)

# Initialize recommender
hybrid = HybridRecommender(
    svd_model=svd_model,
    movies_catalog_path='data/processed/movies_catalog.csv'
)
```

## Core Features & Usage

### 1. Get Recommendations for New Users

**Use Case**: User just signed up and provided genre preferences + rated a few movies.

```python
# User profile
user_ratings = [
    (50, 5),   # Star Wars - loved it
    (181, 5),  # Return of the Jedi - loved it
    (258, 2)   # Contact - didn't like
]
preferred_genres = ['Action', 'Sci-Fi', 'Adventure']

# Get recommendations
recommendations = hybrid.recommend_for_new_user(
    user_ratings=user_ratings,
    preferred_genres=preferred_genres,
    n=10,                      # Number of recommendations
    genre_weight=0.3,          # 30% weight to explicit genres
    rating_weight=0.7,         # 70% weight to rating behavior
    exclude_rated=True,        # Don't recommend already rated movies
    diversity_boost=False      # Set True to increase genre diversity
)

# Output format
# [
#   {
#     'movie_id': 121,
#     'similarity_score': 0.87,
#     'genres': ['Action', 'Sci-Fi']
#   },
#   ...
# ]
```

### 2. Get Recommendations for Existing Users

**Use Case**: User has been using the system and has ratings in the training data.

```python
# Simple - just provide user_id
recommendations = hybrid.recommend_for_existing_user(
    user_id=196,
    n=10
)

# Output: [movie_id_1, movie_id_2, ..., movie_id_10]
```

### 3. Predict Rating for a Specific Movie

**Use Case**: User is viewing a movie detail page - show predicted rating.

```python
# For existing user
prediction = hybrid.predict_rating(
    user_id=196,
    movie_id=50  # Star Wars
)

# For new user
prediction = hybrid.predict_rating(
    user_id=999999,  # New user not in training data
    movie_id=50,
    user_ratings=[(181, 5), (100, 4)],
    preferred_genres=['Action', 'Sci-Fi']
)

# Output format
# {
#   'predicted_rating': 4.2,
#   'confidence': 0.75,
#   'method': 'collaborative_filtering'  # or 'content_based'
# }
```

### 4. Will User Like This Movie? (Binary Classification)

**Use Case**: Show thumbs up/down prediction before user watches.

```python
result = hybrid.will_user_like(
    user_id=196,
    movie_id=50,
    threshold=3.5  # Minimum rating to consider "will like"
)

# Output format
# {
#   'will_like': True,
#   'predicted_rating': 4.2,
#   'confidence': 0.75,
#   'movie_genres': ['Action', 'Adventure', 'Sci-Fi'],
#   'explanation': '✓ You will probably like it (estimated rating: 4.2/5)
#                   • Matches your favorite genres: Action, Sci-Fi
#                   • Based on your 2 previous ratings'
# }
```

### 5. Batch Rating Predictions

**Use Case**: Predict ratings for a whole catalog page efficiently.

```python
movie_ids = [50, 100, 121, 181, 258, 300]

predictions_df = hybrid.batch_predict_ratings(
    user_id=196,
    movie_ids=movie_ids
)

# Output: DataFrame sorted by predicted_rating
#    movie_id  predicted_rating  confidence              method
# 0        50              4.5        0.85  collaborative_filtering
# 1       121              4.2        0.78  collaborative_filtering
# 2       181              4.1        0.82  collaborative_filtering
# ...
```

### 6. Explain Recommendations

**Use Case**: Show users why a movie was recommended.

```python
# First, build user profile
user_profile = hybrid._build_user_profile_hybrid(
    user_ratings=[(50, 5), (181, 5)],
    preferred_genres=['Action', 'Sci-Fi']
)

# Get explanation
explanation = hybrid.explain_recommendation(
    movie_id=121,
    user_profile=user_profile
)

# Output: "Recommended because you like: Action, Sci-Fi, Adventure"
```

## API Integration Example

### FastAPI Endpoint Implementation

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.models.HybridRecommender import HybridRecommender
import mlflow

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

# Load model once at startup
svd_model = mlflow.sklearn.load_model("models:/MovieRatingPredictModel/Production")
hybrid = HybridRecommender(svd_model, "back-end/app/data/movies.csv")

class RecommendationRequest(BaseModel):
    user_id: int
    user_ratings: Optional[List[tuple]] = None
    preferred_genres: Optional[List[str]] = None
    n: int = 10

class RatingPredictionRequest(BaseModel):
    user_id: int
    movie_id: int
    user_ratings: Optional[List[tuple]] = None
    preferred_genres: Optional[List[str]] = None

@router.post("/get-recommendations")
def get_recommendations(request: RecommendationRequest):
    """Get personalized movie recommendations for a user"""
    try:
        # Check if user exists in training data
        if request.user_id in hybrid.svd_model.users_id2index:
            # Existing user - use SVD
            recommendations = hybrid.recommend_for_existing_user(
                user_id=request.user_id,
                n=request.n
            )
        else:
            # New user - use hybrid approach
            recommendations = hybrid.recommend_for_new_user(
                user_ratings=request.user_ratings,
                preferred_genres=request.preferred_genres,
                n=request.n
            )

        return {
            "user_id": request.user_id,
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict-rating")
def predict_rating(request: RatingPredictionRequest):
    """Predict what rating a user would give to a movie"""
    try:
        prediction = hybrid.predict_rating(
            user_id=request.user_id,
            movie_id=request.movie_id,
            user_ratings=request.user_ratings,
            preferred_genres=request.preferred_genres
        )
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/will-like")
def will_like(request: RatingPredictionRequest):
    """Determine if user will like a movie (binary classification)"""
    try:
        result = hybrid.will_user_like(
            user_id=request.user_id,
            movie_id=request.movie_id,
            user_ratings=request.user_ratings,
            preferred_genres=request.preferred_genres,
            threshold=3.5
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Configuration Parameters

### Weight Tuning

```python
# Adjust importance of ratings vs genres
recommendations = hybrid.recommend_for_new_user(
    user_ratings=ratings,
    preferred_genres=genres,
    genre_weight=0.4,   # ↑ More weight to explicit preferences
    rating_weight=0.6   # ↓ Less weight to observed behavior
)
```

**Recommended Settings:**

- **Cold Start** (no ratings): `genre_weight=1.0, rating_weight=0.0`
- **Few Ratings** (1-5): `genre_weight=0.4, rating_weight=0.6`
- **Many Ratings** (10+): `genre_weight=0.2, rating_weight=0.8`

### Diversity Boost

```python
# Enable diversity to avoid recommending only similar genres
recommendations = hybrid.recommend_for_new_user(
    ...,
    diversity_boost=True  # Penalizes over-represented genres
)
```

### Confidence Thresholds

```python
prediction = hybrid.predict_rating(user_id, movie_id)

if prediction['confidence'] < 0.3:
    # Low confidence - ask user for more ratings
    print("⚠️ Need more information to make accurate predictions")
elif prediction['confidence'] < 0.6:
    # Medium confidence
    print("📊 Moderate confidence prediction")
else:
    # High confidence
    print("✓ High confidence prediction")
```

## Data Format Requirements

### Movies Catalog CSV Format

```csv
movie_id,unknown,Action,Adventure,Animation,Children,Comedy,Crime,Documentary,Drama,Fantasy,Film-Noir,Horror,Musical,Mystery,Romance,Sci-Fi,Thriller,War,Western
1,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0
2,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0
3,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0
```

**Columns:**

- `movie_id`: Unique movie identifier
- Genre columns: Binary (0/1) indicating if movie belongs to that genre

### User Ratings Format

```python
user_ratings = [
    (movie_id, rating),
    (50, 5.0),        # Movie 50, rating 5 out of 5
    (100, 4.0),       # Movie 100, rating 4 out of 5
    (258, 2.0)        # Movie 258, rating 2 out of 5
]
```

### Preferred Genres Format

```python
preferred_genres = ['Action', 'Sci-Fi', 'Adventure']
# Must match exactly the genre column names in movies_catalog.csv
```

## Error Handling

```python
try:
    recommendations = hybrid.recommend_for_new_user(
        user_ratings=ratings,
        preferred_genres=genres
    )
except KeyError as e:
    # Movie ID not found in catalog
    print(f"Invalid movie ID: {e}")
except ValueError as e:
    # Invalid genre name
    print(f"Invalid genre: {e}")
except Exception as e:
    # Fallback to popular recommendations
    print(f"Error: {e}")
    recommendations = hybrid._recommend_popular(n=10)
```
