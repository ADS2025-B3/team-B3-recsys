import pandas as pd
import yaml
import mlflow
import os
from svd_impl import SVDCF 
import metrics # Importamos nuestro nuevo módulo de métricas

def load_config(config_path="configs/params.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def run_svd_training():
    config = load_config()
    
    # Setup MLflow
    mlflow.set_tracking_uri(config["main"]["tracking_uri"])
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
        
        # 2. Load Data (Train AND Test)
        print("Loading data...")
        train_df = pd.read_csv(config["data"]["train_path"])
        test_df = pd.read_csv(config["data"]["test_path"]) # Ahora cargamos Test también
        
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
    run_svd_training()