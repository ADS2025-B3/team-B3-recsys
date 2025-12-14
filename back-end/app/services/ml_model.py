"""
Service for loading and using ML models from MLflow
"""
import os
import mlflow
import mlflow.sklearn
from typing import Optional, Any, Dict
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class MLModelService:
    """Service to manage multiple MLflow models for different recommendation types"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}  # Dictionary to store multiple models
        
        # Set MLflow tracking URI and credentials
        mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
        
        # Get credentials from settings (which loads from .env)
        username = settings.MLFLOW_TRACKING_USERNAME
        password = settings.MLFLOW_TRACKING_PASSWORD
        
        # Set them for MLflow
        if username and password:
            os.environ["MLFLOW_TRACKING_USERNAME"] = username
            os.environ["MLFLOW_TRACKING_PASSWORD"] = password
            logger.info(f"MLflow tracking credentials loaded. Username: {username}")
        else:
            logger.warning("MLflow tracking credentials are not set.")
            logger.warning("If MLflow requires authentication, model loading will fail.")
        
        # Model names for different recommendation types
        self.model_names = {
            "rating_prediction": "MovieRatingPredictModel",
            # "user_recommendations": "TopUserRecommendationsModel",
            # "similar_items": "MovieSimilarRecommenderModel",
            # "top_movies": "Top10MoviesModel"
        }
    
    def load_model(self, model_type: str, model_name: str = None, version: str = "latest"):
        """
        Load a specific model from MLflow Model Registry
        
        Args:
            model_type: Type of model - "rating_prediction", "user_recommendations", 
                       "similar_items", or "top_movies"
            model_name: Name of the registered model (uses default if None)
            version: Model version - "latest", version number, or stage name like "Production"
        """
        # Use default model name if not provided
        if model_name is None:
            model_name = self.model_names.get(model_type)
            if model_name is None:
                raise ValueError(f"Invalid model_type: {model_type}")
        
        try:
            # Construct model URI
            if version == "latest":
                model_uri = f"models:/{model_name}/latest"
            elif version.isdigit():
                model_uri = f"models:/{model_name}/{version}"
            else:
                # Assume it's a stage (Production, Staging, etc.)
                model_uri = f"models:/{model_name}/{version}"
            
            logger.info(f"Loading {model_type} model from: {model_uri}")
            self.models[model_type] = mlflow.sklearn.load_model(model_uri)
            logger.info(f"Model loaded successfully: {model_name} ({version}) as {model_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading {model_type} model: {str(e)}")
            raise Exception(f"Failed to load {model_type} model: {str(e)}")
    
    def load_all_models(self):
        """Load all recommendation models"""
        results = {}
        for model_type in self.model_names.keys():
            try:
                self.load_model(model_type)
                results[model_type] = "success"
            except Exception as e:
                logger.warning(f"Failed to load {model_type}: {str(e)}")
                results[model_type] = f"failed: {str(e)}"
        return results
    
    def predict_score(self, user_id: int, item_id: int):
        """
        Predict rating score for a user-item pair
        Uses the rating_prediction model
        
        Args:
            user_id: User ID
            item_id: Item/Movie ID
            
        Returns:
            Predicted rating score
        """
        model = self.models.get("rating_prediction")
        if model is None:
            raise ValueError("Rating prediction model not loaded. Call load_model('rating_prediction') first.")
        
        try:
            prediction = model.predict_score(user_id, item_id)
            return float(prediction)
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            raise
    
    def recommend_top_n(self, user_id: int, n: int = 10):
        """
        Get top N personalized recommendations for a user
        Uses the user_recommendations model
        
        Args:
            user_id: User ID
            n: Number of recommendations
            
        Returns:
            List of recommended movie IDs
        """
        model = self.models.get("user_recommendations")
        if model is None:
            raise ValueError("User recommendations model not loaded. Call load_model('user_recommendations') first.")
        
        try:
            recommendations = model.recommend_top_n(user_id, n=n)
            return recommendations
        except Exception as e:
            logger.error(f"Recommendation error: {str(e)}")
            raise
    
    def recommend_similar_items(self, item_id: int, n: int = 10):
        """
        Get similar items to a given item
        Uses the similar_items model
        
        Args:
            item_id: Item/Movie ID
            n: Number of similar items to return
            
        Returns:
            List of tuples (item_id, similarity_score)
        """
        model = self.models.get("similar_items")
        if model is None:
            raise ValueError("Similar items model not loaded. Call load_model('similar_items') first.")
        
        try:
            similar_items = model.recommend_similar_items(item_id, n=n)
            return similar_items
        except Exception as e:
            logger.error(f"Similar items error: {str(e)}")
            raise
    
    def get_top_movies(self, n: int = 10):
        """
        Get top N globally popular movies
        Uses the top_movies model
        
        Args:
            n: Number of top movies
            
        Returns:
            List of top movie IDs
        """
        model = self.models.get("top_movies")
        if model is None:
            raise ValueError("Top movies model not loaded. Call load_model('top_movies') first.")
        
        try:
            top_movies = model.get_top_movies(n=n)
            return top_movies
        except Exception as e:
            logger.error(f"Top movies error: {str(e)}")
            raise


# Singleton instance
ml_service = MLModelService()
