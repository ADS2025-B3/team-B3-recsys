"""
Grid Search for SVD Hyperparameters
Finds the best num_components for the SVD model.
"""

import pandas as pd
import yaml
import os
from svd_impl import SVDCF
import metrics
from train_svd import load_config
import mlflow

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

def grid_search_svd(n_components_range=None, top_n=10):
    """
    Perform grid search to find optimal num_components.
    
    :param n_components_range: List of num_components to try (e.g., [10, 20, 30, 50, 100])
    :param top_n: Number of recommendations for evaluation
    """
    
    if n_components_range is None:
        n_components_range = [5, 10, 15, 20, 30, 50, 75, 100]
    
    config = load_config()
    
    # Load data once
    print("Loading data...")
    train_path = os.path.join(PROJECT_ROOT, config["data"]["train_path"])
    train_df = pd.read_csv(train_path)
    
    test_path = os.path.join(PROJECT_ROOT, config["data"]["test_path"])
    test_df = pd.read_csv(test_path)
    
    # Configure MLflow
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(f"{config['main']['project_name']}_grid_search")
    
    results = []
    best_map = 0
    best_config = None
    
    print(f"\n{'='*60}")
    print(f"Starting Grid Search for num_components")
    print(f"Testing values: {n_components_range}")
    print(f"{'='*60}\n")
    
    for n_comp in n_components_range:
        print(f"\n{'─'*60}")
        print(f"Testing num_components = {n_comp}")
        print(f"{'─'*60}")
        
        with mlflow.start_run(run_name=f"GridSearch_k{n_comp}"):
            # Log parameters
            mlflow.log_param("num_components", n_comp)
            mlflow.log_param("top_n", top_n)
            mlflow.log_param("grid_search", True)
            
            # Train model
            print("Training...")
            model = SVDCF(num_components=n_comp)
            model.fit(train_df)
            
            # Evaluate RMSE
            print("Evaluating RMSE...")
            rmse = metrics.evaluate_rmse(model.predict_score, train_df, test_df)
            mlflow.log_metric("rmse", rmse)
            
            # Evaluate Ranking
            print(f"Evaluating Ranking Metrics (@{top_n})...")
            ranking_metrics = metrics.evaluate_algorithm_top(
                test_df, 
                model, 
                at=top_n
            )
            mlflow.log_metrics(ranking_metrics)
            
            # Store results
            result = {
                'num_components': n_comp,
                'rmse': rmse,
                'precision': ranking_metrics['precision'],
                'recall': ranking_metrics['recall'],
                'map': ranking_metrics['map']
            }
            results.append(result)
            
            print(f"\nResults for k={n_comp}:")
            print(f"  RMSE:      {rmse:.4f}")
            print(f"  Precision: {ranking_metrics['precision']:.4f}")
            print(f"  Recall:    {ranking_metrics['recall']:.4f}")
            print(f"  MAP:       {ranking_metrics['map']:.4f}")
            
            # Track best
            if ranking_metrics['map'] > best_map:
                best_map = ranking_metrics['map']
                best_config = n_comp
                mlflow.log_param("is_best", True)
    
    # Print summary
    print(f"\n{'='*60}")
    print("GRID SEARCH SUMMARY")
    print(f"{'='*60}\n")
    
    results_df = pd.DataFrame(results)
    print(results_df.to_string(index=False))
    
    print(f"\n{'='*60}")
    print(f"🏆 BEST CONFIGURATION:")
    print(f"  num_components = {best_config}")
    print(f"  MAP = {best_map:.4f}")
    print(f"{'='*60}\n")
    
    # Save results to CSV
    results_path = os.path.join(PROJECT_ROOT, "outputs", "grid_search_results.csv")
    os.makedirs(os.path.dirname(results_path), exist_ok=True)
    results_df.to_csv(results_path, index=False)
    print(f"Results saved to: {results_path}")
    
    return best_config, results_df

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(os.path.join(SCRIPT_DIR, '.env'))
    
    # Run grid search
    best_k, results = grid_search_svd(
        n_components_range=[10, 15, 20, 30, 50],
        top_n=10
    )
    
    print(f"\n✅ Grid search complete!")
    print(f"Update your params.yaml with: num_components: {best_k}")
