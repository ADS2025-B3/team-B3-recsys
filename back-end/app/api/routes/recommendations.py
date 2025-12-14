"""
Recommendations API endpoints using MLflow models
"""
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.ml_model import ml_service
from app.api.deps import get_current_user, SessionDep
from app.models.user import User
from app.models import MovieRead
from app import crud

router = APIRouter()


# ============================================================================
# Public Endpoints - Used by Frontend
# ============================================================================

@router.get("/user", response_model=List[MovieRead])
def get_user_recommendations(
    session: SessionDep,
    n: int = 10,
    current_user: User = Depends(get_current_user)
):
    """
    Get personalized movie recommendations for the current user
    """
    try:
        # Get recommended movie IDs from ML model
        movie_ids = ml_service.recommend_top_n(user_id=current_user.id, n=n)
        
        # Get movie details from database
        movies = []
        for mid in movie_ids:
            movie = crud.movie.movie_crud.get(session, mid)
            if movie:
                movies.append(movie)
        
        return movies
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@router.get("/global", response_model=List[MovieRead])
def get_global_recommendations(
    session: SessionDep,
    n: int = 10
):
    """
    Get top N globally popular movies (no authentication required)
    """
    try:
        # Get top movie IDs from ML model
        movie_ids = ml_service.get_top_movies(n=n)
        
        # Get movie details from database
        movies = []
        for mid in movie_ids:
            movie = crud.movie.movie_crud.get(session, mid)
            if movie:
                movies.append(movie)
        
        return movies
    except ValueError as e:
        # If model not loaded, return most rated movies from database
        from sqlmodel import select, func
        from app.models.rating import Rating
        from app.models.movie import Movie
        
        statement = (
            select(Movie)
            .join(Rating, Movie.id == Rating.movie_id)
            .group_by(Movie.id)
            .order_by(func.count(Rating.id).desc())
            .limit(n)
        )
        movies = session.exec(statement).all()
        return movies
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get global recommendations: {str(e)}")


@router.get("/movies/{movie_id}/similar", response_model=List[MovieRead])
def get_similar_movies(
    session: SessionDep,
    movie_id: int,
    n: int = 10
):
    """
    Get similar movies based on a movie ID
    """
    try:
        # Get similar movie IDs from ML model
        similar_items = ml_service.recommend_similar_items(item_id=movie_id, n=n)
        
        # Get movie details from database
        movie_ids = [item_id for item_id, score in similar_items]
        movies = []
        for mid in movie_ids:
            movie = crud.movie.movie_crud.get(session, mid)
            if movie:
                movies.append(movie)
        
        return movies
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@router.get("/movies/{movie_id}/predict")
def predict_movie_rating(
    session: SessionDep,
    movie_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Predict the rating a user would give to a movie
    """
    try:
        predicted_score = ml_service.predict_score(
            user_id=current_user.id,
            item_id=movie_id
        )
        
        return {
            "movie_id": movie_id,
            "predicted_rating": float(predicted_score)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/movies/{movie_id}/similar", response_model=List[MovieRead])
def get_similar_movies(
    session: SessionDep,
    movie_id: int,
    n: int = 10
):
    """
    Get similar movies based on a movie ID
    """
    try:
        # Get similar movie IDs from ML model
        similar_items = ml_service.recommend_similar_items(item_id=movie_id, n=n)
        
        # Get movie details from database
        movie_ids = [item_id for item_id, score in similar_items]
        movies = []
        for mid in movie_ids:
            movie = crud.movie.movie_crud.get(session, mid)
            if movie:
                movies.append(movie)
        
        return movies
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@router.get("/movies/{movie_id}/predict")
def predict_movie_rating(
    session: SessionDep,
    movie_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Predict the rating a user would give to a movie
    """
    try:
        predicted_score = ml_service.predict_score(
            user_id=current_user.id,
            item_id=movie_id
        )
        
        return {
            "movie_id": movie_id,
            "predicted_rating": float(predicted_score)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


# ============================================================================
# Admin/Testing Endpoints - For managing models
# ============================================================================

@router.post("/load-model")
def load_model(
    model_type: str,
    model_name: str = None,
    version: str = "latest",
    current_user: User = Depends(get_current_user)
):
    """
    Load or reload a specific model from MLflow
    
    model_type options:
    - rating_prediction: Predict ratings for user-item pairs
    - user_recommendations: Get personalized recommendations for users
    - similar_items: Find similar movies
    - top_movies: Get globally popular movies
    """
    try:
        ml_service.load_model(model_type=model_type, model_name=model_name, version=version)
        return {
            "status": "success",
            "message": f"Model loaded: {model_type} (version: {version})"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")


@router.post("/load-all-models")
def load_all_models(
    current_user: User = Depends(get_current_user)
):
    """
    Load all recommendation models from MLflow
    """
    try:
        results = ml_service.load_all_models()
        return {
            "status": "completed",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load models: {str(e)}")
