from fastapi import FastAPI
import logging
from contextlib import asynccontextmanager

from Scheduler import setup_scheduler, start_scheduler, shutdown_scheduler
from DBConnection import test_connection
from Settings import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting retraining service...")
    
    # Test database connection
    if test_connection():
        logger.info("Database connection verified")
    else:
        logger.error("Failed to connect to database")
    
    # Setup and start scheduler
    setup_scheduler()
    start_scheduler()
    
    yield
    
    # Shutdown
    shutdown_scheduler()
    logger.info("Retraining service stopped")


app = FastAPI(
    title="Model Retraining Service",
    lifespan=lifespan
)


@app.get("/health")
def health_check():
    return test_connection()


@app.post("/trigger-retraining")
async def trigger_retraining():
    """Manually trigger model retraining"""
    from Scheduler import retrain_models_job
    await retrain_models_job()
    return {"status": "Retraining job triggered"}