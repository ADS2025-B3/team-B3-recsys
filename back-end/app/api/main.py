""" Main API routes definition """
from fastapi import APIRouter
from app.api.routes import (
    general,
    login,
    users,
    movies,
    ratings,
    user_preferences,
    recommendations
)


api_router = APIRouter()
api_router.include_router(general.router, tags=["general"])
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, tags=["user"], prefix="/auth")
api_router.include_router(movies.router, tags=["Movies"], prefix="/movies")
api_router.include_router(ratings.router, tags=["Ratings"], prefix="/ratings")
api_router.include_router(user_preferences.router, tags=["User Preferences"], prefix="/user_preferences")
api_router.include_router(recommendations.router, tags=["Recommendations"], prefix="/recommendations")