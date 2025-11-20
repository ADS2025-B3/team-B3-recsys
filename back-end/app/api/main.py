""" Main API routes definition """
from fastapi import APIRouter


from app.api.routes import general

api_router = APIRouter()
api_router.include_router(general.router, tags=["general"])