import pandas as pd
import yaml
import mlflow
import os
from svd_impl import SVDCF 
import metrics # Importamos nuestro nuevo módulo de métricas
from dotenv import load_dotenv

# Use absolute paths based on script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

def load_config(config_path=None):
    if config_path is None:
        config_path = os.path.join(PROJECT_ROOT, "configs", "params.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def run_svd_training():
    config = load_config()
    
   # --- FIX: Explicitly set environment variables for Docker stability ---
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    os.environ["MLFLOW_TRACKING_URI"] = tracking_uri
    os.environ["MLFLOW_TRACKING_USERNAME"] = os.getenv("MLFLOW_TRACKING_USERNAME", "")
    os.environ["MLFLOW_TRACKING_PASSWORD"] = os.getenv("MLFLOW_TRACKING_PASSWORD", "")
    # ----------------------------------------------------------------------
    print(f"Loaded MLFLOW_TRACKING_URI: {os.getenv('MLFLOW_TRACKING_URI')}")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(config["main"]["project_name"])
    
    print("Starting SVD Training Run...")

    run_name_dynamic = f"SVD_k{config['svd_model']['num_components']}_top{config['svd_model']['top_n']}"
    
    with mlflow.start_run(run_name=run_name_dynamic):
        # 1. Log Params
        n_components = config["svd_model"]["num_components"]
        top_n = config["svd_model"]["top_n"]
        
        mlflow.log_param("model_type", "SVD")
        mlflow.log_param("num_components", n_components)
        mlflow.log_param("top_n", top_n)
        
        # 2. Load Data (Train AND Test) - Using absolute paths
        print("Loading data...")
        train_path = os.path.join(PROJECT_ROOT, config["data"]["train_path"])
        train_df = pd.read_csv(train_path)
        
        test_path = os.path.join(PROJECT_ROOT, config["data"]["test_path"])
        test_df = pd.read_csv(test_path) 
        
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

if __name__ == "__main__":
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
    run_svd_training()