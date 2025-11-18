import mlflow
from mlflow import sklearn
import sklearn.linear_model
import os

def main():
    # 1. Connect to MLflow server
    mlflow.set_tracking_uri("http://localhost:5500")

    # 2. Create / select experiment
    mlflow.set_experiment("mlflow_test_experiment")

    # 3. Start an MLflow run
    with mlflow.start_run(run_name="test_run") as run:

        # Log parameters
        mlflow.log_param("learning_rate", 0.01)
        mlflow.log_param("optimizer", "sgd")

        # Log metrics
        mlflow.log_metric("rmse", 0.12)
        mlflow.log_metric("mae", 0.07)

        # Log an artifact file
        with open("info.txt", "w") as f:
            f.write("This is a test artifact logged with MLflow.")
        mlflow.log_artifact("info.txt")

        # Log a simple model
        model = sklearn.linear_model.LinearRegression()
        sklearn.log_model(model, "model")

        # Print run URL
        print("Run logged successfully!")
        print(f"Run ID: {run.info.run_id}")
        print(f"View it at: http://localhost:6000/#/experiments/{run.info.experiment_id}/runs/{run.info.run_id}")

    # Cleanup artifact test file
    os.remove("info.txt")

if __name__ == "__main__":
    main()

