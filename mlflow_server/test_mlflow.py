import mlflow
import mlflow.sklearn
from sklearn.linear_model import LinearRegression
import os

def main():
    # Connect to MLflow server
    mlflow.set_tracking_uri("http://localhost:5500")
    mlflow.set_experiment("test_experiment")

    with mlflow.start_run(run_name="example_run") as run:
        # Log parameters
        mlflow.log_param("learning_rate", 0.01)

        # Log metrics
        mlflow.log_metric("rmse", 0.1)

        # Log an artifact
        artifact_file = "info.txt"
        with open(artifact_file, "w") as f:
            f.write("Artifact for MLflow logging")
        mlflow.log_artifact(artifact_file)

        # ✅ Log scikit-learn model correctly
        model = LinearRegression()
        mlflow.sklearn.log_model(model, artifact_path="linear_model")

        print("Run logged successfully!")
        print(f"Run ID: {run.info.run_id}")
        print(f"View at: http://localhost:5500/#/experiments/{run.info.experiment_id}/runs/{run.info.run_id}")

        # Cleanup
        os.remove(artifact_file)

if __name__ == "__main__":
    main()

