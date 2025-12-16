from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlmodel import Session, select
import logging
import pandas as pd
from Models import User, Rating
from DBConnection import engine
from train_svd_user import run_svd_user_training

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def retrain_models_job():
    """Job to retrain ML models nightly"""
    try:
        logger.info("Starting nightly model retraining...")
        
        with Session(engine) as session:
            # Get all users and their ratings to retrain models
            users = session.exec(select(User)).all()
            ratings = session.exec(select(Rating)).all()
            
            logger.info(f"Retrieved {len(users)} users and {len(ratings)} ratings")
            
            # Convert to DataFrame for training
            ratings_df = pd.DataFrame([
                {
                    "user_id": int(r.user_id),
                    "movie_id": int(r.movie_id),
                    "rating": int(r.rating),
                    "timestamp": r.created_at
                }
                for r in ratings
            ])
            # filter users with id > 10000
            ratings_df = ratings_df[ratings_df['user_id'] >= 10000]
            logger.info(f"Prepared dataset with {len(ratings_df['rating'])} ratings")
            
            # import original dataset
            TRAIN_CSV_FILEPATH = 'data/train.csv' 
            TEST_CSV_FILEPATH = 'data/test.csv'
            train = pd.read_csv(TRAIN_CSV_FILEPATH)
            test = pd.read_csv(TEST_CSV_FILEPATH) 
            config = {
                "model": {
                    "svd": {
                        "n_components": 20,
                        "top_n": 10
                    }
                },
                "main": {
                    "project_name": "hybrid_recommender_experiment",
                    "random_seed": 42
                }
            }
            #rename item_id to movie_id
            train = train.rename(columns={"item_id": "movie_id"})
            test = test.rename(columns={"item_id": "movie_id"})
            
            #concatenate ratings_df with train
            train = pd.concat([train, ratings_df], ignore_index=True)
            
            # Retrain SVD User model
            logger.info("Retraining SVD User model...")
            run_svd_user_training(
                config=config,
                train=train,
                test=test,
                top_n=10,
                n_components=20
            )
            
            logger.info("Nightly retraining completed successfully")
            
        
    except Exception as e:
        logger.error(f"Error during nightly model retraining: {e}", exc_info=True)


def setup_scheduler():
    """Configure scheduled jobs"""
    # Ejecutar cada noche a las 2:00 AM
    scheduler.add_job(
        retrain_models_job,
        trigger=CronTrigger(hour=2, minute=0),
        id="retrain_models",
        name="Retrain ML models nightly",
        replace_existing=True
    )
    
    logger.info("Scheduler configured: Model retraining at 2:00 AM daily")


def start_scheduler():
    """Start the scheduler"""
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")


def shutdown_scheduler():
    """Shutdown the scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")