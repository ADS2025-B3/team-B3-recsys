"""
Service for loading and using ML models from MLflow with Hybrid Recommendations
"""
import os
import mlflow
import mlflow.sklearn
from typing import Optional, Any, Dict, List, Tuple
from app.core.config import settings
from app.services.recommenders.HybridRecommender import HybridRecommender
import logging

logger = logging.getLogger(__name__)


class MLModelService:
    """Service to manage MLflow models with Hybrid Recommendation System"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}  # Dictionary to store multiple models
        self.hybrid_recommender: Optional[HybridRecommender] = None
        
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
            "svd_model": "MovieRatingPredictModel",
            "similar_items": "MovieSimilarRecommenderModel",
        }
        
        # Path to movies catalog (required for HybridRecommender)
        self.movies_catalog_path = os.path.join(settings.BASE_DIR, "app", "data", "movies.csv")
    
    def load_model(self, model_type: str, model_name: str = None, version: str = "latest"):
        """
        Load a specific model from MLflow Model Registry
        
        Args:
            model_type: Type of model - "svd_model" or "similar_items"
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
            
            # If loading SVD model, initialize HybridRecommender
            if model_type == "svd_model":
                self._initialize_hybrid_recommender()
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading {model_type} model: {str(e)}")
            raise Exception(f"Failed to load {model_type} model: {str(e)}")
    
    def _initialize_hybrid_recommender(self):
        """Initialize HybridRecommender with loaded SVD model"""
        svd_model = self.models.get("svd_model")
        if svd_model is None:
            logger.warning("Cannot initialize HybridRecommender: SVD model not loaded")
            return
        
        try:
            if not os.path.exists(self.movies_catalog_path):
                logger.warning(f"Movies catalog not found at {self.movies_catalog_path}")
                logger.warning("HybridRecommender will not be available")
                return
            
            self.hybrid_recommender = HybridRecommender(
                svd_model=svd_model,
                movies_catalog_path=self.movies_catalog_path
            )
            logger.info("HybridRecommender initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing HybridRecommender: {str(e)}")
            self.hybrid_recommender = None
    
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
    
    def predict_score(self, user_id: int, item_id: int, 
                     user_ratings: Optional[List[Tuple[int, float]]] = None,
                     preferred_genres: Optional[List[str]] = None):
        """
        Predict rating score for a user-item pair using HybridRecommender
        Works for both existing and new users
        
        Args:
            user_id: User ID
            item_id: Item/Movie ID
            user_ratings: Optional list of tuples [(movie_id, rating), ...] for new users
            preferred_genres: Optional list of preferred genres for new users
            
        Returns:
            Dict with predicted_rating, confidence, and method
        """
        if self.hybrid_recommender is None:
            raise ValueError("HybridRecommender not initialized. Load SVD model first.")
        
        try:
            prediction = self.hybrid_recommender.predict_rating(
                user_id=user_id,
                movie_id=item_id,
                user_ratings=user_ratings,
                preferred_genres=preferred_genres
            )
            return prediction
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            raise
    
    def recommend_top_n(self, user_id: int, n: int = 10,
                       user_ratings: Optional[List[Tuple[int, float]]] = None,
                       preferred_genres: Optional[List[str]] = None,
                       genre_weight: float = 0.3,
                       rating_weight: float = 0.7,
                       diversity_boost: bool = False):
        """
        Get top N personalized recommendations for a user using HybridRecommender
        Automatically handles both existing and new users
        
        Args:
            user_id: User ID
            n: Number of recommendations
            user_ratings: Optional ratings for new users [(movie_id, rating), ...]
            preferred_genres: Optional list of preferred genres for new users
            genre_weight: Weight for explicit genre preferences (0-1)
            rating_weight: Weight for rating behavior (0-1)
            diversity_boost: Whether to increase genre diversity
            
        Returns:
            List of recommended movie IDs or dicts with additional info
        """
        if self.hybrid_recommender is None:
            raise ValueError("HybridRecommender not initialized. Load SVD model first.")
        
        try:
            svd_model = self.models.get("svd_model")
            
            # Check if user exists in training data
            if user_id in svd_model.users_id2index:
                # Existing user - use SVD
                recommendations = self.hybrid_recommender.recommend_for_existing_user(
                    user_id=user_id,
                    n=n
                )
            else:
                # New user - use hybrid approach
                recommendations = self.hybrid_recommender.recommend_for_new_user(
                    user_ratings=user_ratings,
                    preferred_genres=preferred_genres,
                    n=n,
                    genre_weight=genre_weight,
                    rating_weight=rating_weight,
                    diversity_boost=diversity_boost
                )
            
            return recommendations
        except Exception as e:
            logger.error(f"Recommendation error: {str(e)}")
            raise
    
    def will_user_like(self, user_id: int, movie_id: int,
                      user_ratings: Optional[List[Tuple[int, float]]] = None,
                      preferred_genres: Optional[List[str]] = None,
                      threshold: float = 3.5):
        """
        Determine if a user will like a movie (binary classification)
        
        Args:
            user_id: User ID
            movie_id: Movie ID
            user_ratings: Optional ratings for new users
            preferred_genres: Optional genres for new users
            threshold: Minimum rating to consider "will like" (default 3.5)
            
        Returns:
            Dict with will_like (bool), predicted_rating, confidence, genres, explanation
        """
        if self.hybrid_recommender is None:
            raise ValueError("HybridRecommender not initialized. Load SVD model first.")
        
        try:
            result = self.hybrid_recommender.will_user_like(
                user_id=user_id,
                movie_id=movie_id,
                user_ratings=user_ratings,
                preferred_genres=preferred_genres,
                threshold=threshold
            )
            return result
        except Exception as e:
            logger.error(f"Like prediction error: {str(e)}")
            raise
    
    def batch_predict_ratings(self, user_id: int, movie_ids: List[int],
                             user_ratings: Optional[List[Tuple[int, float]]] = None,
                             preferred_genres: Optional[List[str]] = None):
        """
        Predict ratings for multiple movies at once
        
        Args:
            user_id: User ID
            movie_ids: List of movie IDs
            user_ratings: Optional ratings for new users
            preferred_genres: Optional genres for new users
            
        Returns:
            DataFrame with movie_id, predicted_rating, confidence, method
        """
        if self.hybrid_recommender is None:
            raise ValueError("HybridRecommender not initialized. Load SVD model first.")
        
        try:
            predictions_df = self.hybrid_recommender.batch_predict_ratings(
                user_id=user_id,
                movie_ids=movie_ids,
                user_ratings=user_ratings,
                preferred_genres=preferred_genres
            )
            return predictions_df.to_dict(orient='records')
        except Exception as e:
            logger.error(f"Batch prediction error: {str(e)}")
            raise
    
    def recommend_similar_items(self, item_id: int, n: int = 10):
        """
        Get similar items to a given item
        Uses the SVD model's item similarity
        
        Args:
            item_id: Item/Movie ID
            n: Number of similar items to return
            
        Returns:
            List of tuples (item_id, similarity_score)
        """
        svd_model = self.models.get("svd_model")
        if svd_model is None:
            raise ValueError("SVD model not loaded. Call load_model('svd_model') first.")
        
        try:
            similar_items = svd_model.recommend_similar_items(item_id, n=n)
            return similar_items
        except Exception as e:
            logger.error(f"Similar items error: {str(e)}")
            raise
    
    def get_popular_movies(self, n: int = 10):
        """
        Get top N globally popular movies using HybridRecommender's fallback
        
        Args:
            n: Number of top movies
            
        Returns:
            List of popular movie IDs
        """
        if self.hybrid_recommender is None:
            raise ValueError("HybridRecommender not initialized. Load SVD model first.")
        
        try:
            popular_movies = self.hybrid_recommender._recommend_popular(n=n)
            return popular_movies
        except Exception as e:
            logger.error(f"Popular movies error: {str(e)}")
            raise


# Singleton instance
ml_service = MLModelService()
