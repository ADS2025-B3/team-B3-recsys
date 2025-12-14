from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
import sentry_sdk # type: ignore
import logging

from app.api.main import api_router
from app.core.config import settings
from app.services.ml_model import ml_service

logger = logging.getLogger(__name__)


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(
        dsn=str(settings.SENTRY_DSN),
        enable_tracing=True,
        send_default_pii=True,
        traces_sample_rate=1.0,                 # To reduce the volume of performance data captured, change traces_sample_rate to a value between 0 and 1
        profile_session_sample_rate=1.0,
        profile_lifecycle="trace"
        )

app = FastAPI(
    title=settings.PROJECT_NAME,
    #openapi_url=None if settings.ENVIRONMENT != "local" else "/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    """Load ML models on startup"""
    try:
        logger.info("Loading ML models from MLflow...")
        results = ml_service.load_all_models()
        
        # Log results
        success_count = sum(1 for r in results.values() if r == "success")
        logger.info(f"ML models loaded: {success_count}/{len(results)} successful")
        
        for model_type, result in results.items():
            if result == "success":
                logger.info(f"  ✓ {model_type}: loaded")
            else:
                logger.warning(f"  ✗ {model_type}: {result}")
                
    except Exception as e:
        logger.warning(f"Error during model loading: {e}")
        logger.warning("Models can be loaded later via /recommendations/load-model or /recommendations/load-all-models endpoints")
