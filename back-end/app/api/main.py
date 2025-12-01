""" Main API routes definition """
from fastapi import APIRouter


from app.api.routes import (
    general,
    login,
    users
)

api_router = APIRouter()
api_router.include_router(general.router, tags=["general"])
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, tags=["user"], prefix="/auth")