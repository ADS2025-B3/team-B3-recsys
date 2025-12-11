import pandas as pd
import yaml
import mlflow
import os
from svd_impl import SVDCF
from dotenv import load_dotenv

# Use absolute paths based on script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

def load_config(config_path=None):
    """Load project configuration from YAML file."""
    if config_path is None:
        config_path = os.path.join(PROJECT_ROOT, "configs", "params.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def load_movie_titles(path=None):
    """
    Helper to load movie titles for better readability in logs.
    Returns a dictionary: {movie_id: title_string}
    """
    if path is None:
        path = os.path.join(PROJECT_ROOT, "data", "raw", "u.item")
    
    try:
        # MovieLens u.item: movie_id|title|...
        # Using latin-1 encoding due to dataset age
        df = pd.read_csv(path, sep='|', encoding='latin-1', header=None, usecols=[0, 1])
        df.columns = ['movie_id', 'title']
        return dict(zip(df.movie_id, df.title))
    except FileNotFoundError:
        print(f"Warning: {path} not found. Logs will show IDs only.")
        return {}

def run_item_similarity_experiment():
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
    
    # Dynamic Run Name for MLflow
    n_components = config["item_rec_model"]["num_components"]
    run_name_dynamic = f"ItemBased_SVD_k{n_components}"
    
    print(f"Starting Item-Based Experiment: {run_name_dynamic}")
    
    with mlflow.start_run(run_name=run_name_dynamic):
        
        # 2. Log Parameters
        mlflow.log_param("model_type", "SVD_Item_Similarity")
        mlflow.log_param("num_components", n_components)
        mlflow.log_param("test_movie_ids", config["item_rec_model"]["test_movie_ids"])
        
        # 3. Load Data & Fit Model (using absolute paths)
        print("Loading data and training model...")
        train_path = os.path.join(PROJECT_ROOT, config["data"]["train_path"])
        train_df = pd.read_csv(train_path)
        titles_map = load_movie_titles()
        
        model = SVDCF(num_components=n_components)
        model.fit(train_df)
        
        # 4. Generate Qualitative Report
        # Since we don't have ground truth for "similarity", we generate a report
        # to be manually inspected in MLflow artifacts.
        report_lines = []
        report_lines.append("=== Item-Based Similarity Report ===\n")
        
        test_ids = config["item_rec_model"]["test_movie_ids"]
        num_sim = config["item_rec_model"]["num_similar"]
        
        print("Generating recommendations...")
        for mid in test_ids:
            # Resolve Title
            query_title = titles_map.get(mid, f"Movie ID {mid}")
            header = f"Query: '{query_title}' (ID: {mid})"
            report_lines.append(header)
            print(header)
            
            # Get Recommendations
            recs = model.recommend_similar_items(mid, n=num_sim)
            
            for rank, (rec_id, score) in enumerate(recs, 1):
                rec_title = titles_map.get(rec_id, f"ID {rec_id}")
                line = f"   {rank}. {rec_title:<40} | Similarity: {score:.4f}"
                report_lines.append(line)
                print(line)
            
            report_lines.append("-" * 50)

        # 5. Save Report as Artifact in MLflow
        # This allows the Data Scientist to "see" the results in the UI
        report_path = "similarity_report.txt"
        with open(report_path, "w") as f:
            f.writelines(line + "\n" for line in report_lines)
        
        mlflow.log_artifact(report_path)
        print(f"Report saved to MLflow artifacts: {report_path}")
        
        # Cleanup local file
        if os.path.exists(report_path):
            os.remove(report_path)

if __name__ == "__main__":
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
    print(f"Loaded MLFLOW_TRACKING_URI: {os.getenv('MLFLOW_TRACKING_URI')}")
    run_item_similarity_experiment()