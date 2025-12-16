import pandas as pd
import yaml
import mlflow
import os
from svd.svd_impl import SVDCF 
import svd.metrics as metrics
from dotenv import load_dotenv



def run_svd_user_training(config,train,test,n_components, top_n,):
    """
    Train SVD model with optional parameter override.
    
    :param n_components: Number of latent factors (overrides config if provided)
    :param top_n: Number of recommendations for evaluation (overrides config if provided)
    """
    
    # --- FIX: Explicitly set environment variables for Docker stability ---
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    print(f"Looking for .env at: {env_path}")
    print(f"File exists: {os.path.exists(env_path)}")
    
    load_dotenv(env_path)
    
    # Verificar que se cargaron las variables
    print(f"MLFLOW_TRACKING_URI loaded: {os.getenv('MLFLOW_TRACKING_URI')}")
    print(f"MLFLOW_TRACKING_USERNAME loaded: {bool(os.getenv('MLFLOW_TRACKING_USERNAME'))}")
    
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    if not tracking_uri:
        raise ValueError("MLFLOW_TRACKING_URI environment variable not set")
    
    os.environ["MLFLOW_TRACKING_URI"] = tracking_uri
    os.environ["MLFLOW_TRACKING_USERNAME"] = os.getenv("MLFLOW_TRACKING_USERNAME", "")
    os.environ["MLFLOW_TRACKING_PASSWORD"] = os.getenv("MLFLOW_TRACKING_PASSWORD", "")
    # ----------------------------------------------------------------------
    print(f"Loaded MLFLOW_TRACKING_URI: {os.getenv('MLFLOW_TRACKING_URI')}")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(config["main"]["project_name"])
    
    # Use provided parameters or fall back to config
    n_components = n_components 
    top_n = top_n 
    
    print("Starting SVD Training Run...")

    run_name_dynamic = f"SVD_k{n_components}_top{top_n}"
    
    with mlflow.start_run(run_name=run_name_dynamic):
        # 1. Log Params
        mlflow.log_param("model_type", "SVD")
        mlflow.log_param("num_components", n_components)
        mlflow.log_param("top_n", top_n)
        mlflow.log_param("random_seed", config["main"].get("random_seed", 42))
     
        
        # 2. Load Data (Train AND Test) - Using absolute paths
        print("Loading data...")
        train_df = train
        test_df = test
        
        # 3. Fit model
        print("Training model...")
        model = SVDCF(num_components=n_components)
        model.fit(train_df)
        
        # 4. Evaluation 1: RMSE (Predicción de nota exacta)
        # Esto nos dice cuánto nos equivocamos prediciendo si pondrá un 4 o un 5
        print("Calculating RMSE...")
        rmse_score = metrics.evaluate_rmse(model.predict_score, train_df, test_df)
        print(f"RMSE: {rmse_score:.4f}")
        mlflow.log_metric("rmse", rmse_score)
        
        # 5. Evaluation 2: Ranking (Precision/Recall/MAP)
        # Esto nos dice si las películas recomendadas son buenas de verdad
        print(f"Calculating Ranking Metrics (@{top_n})...")
        ranking_metrics = metrics.evaluate_algorithm_top(
            test_df, 
            model, 
            at=top_n
        )
        
        # Logueamos todas las métricas de golpe
        print(f"Ranking metrics: {ranking_metrics}")
        mlflow.log_metrics(ranking_metrics)
        
        # 6. Sample output (Visual validation)
        sample_user = train_df.user_id.iloc[0]
        recs = model.recommend_top_n(sample_user, n=top_n)
        print(f"\nExample User {sample_user} recommendations: {recs}")
        
        # 7. Log additional metrics
        print("Calculating additional metrics...")
        
        # Coverage: % of catalog that gets recommended
        all_recommended = set()
        sample_users = train_df.user_id.unique()[:100]  # Sample 100 users
        for user in sample_users:
            recs = model.recommend_top_n(user, n=top_n)
            all_recommended.update(recs)
        
        total_movies = train_df.movie_id.nunique()
        coverage = len(all_recommended) / total_movies
        mlflow.log_metric("catalog_coverage", coverage)
        print(f"Catalog coverage: {coverage:.2%}")
        
        # 8. Save the trained model to MLflow
        print("Saving model to MLflow...")
        model_info = mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name="MovieRatingPredictModel",
            signature=mlflow.models.infer_signature(
                train_df[['user_id', 'movie_id']], 
                train_df['rating']
            )
        )
     

if __name__ == "__main__":
   
    
    run_svd_user_training()