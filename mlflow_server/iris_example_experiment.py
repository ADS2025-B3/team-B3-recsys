import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
import os

# -----------------------------
# 1. Set MLflow tracking server
# -----------------------------
MLFLOW_TRACKING_URI = "http://localhost:5500"  # Replace if your server is different
EXPERIMENT_NAME = "iris_example_experiment"

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)

# -----------------------------
# 2. Load dataset
# -----------------------------
iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, test_size=0.2, random_state=42
)

# -----------------------------
# 3. Define hyperparameters
# -----------------------------
params = {
    "n_estimators": 100,
    "max_depth": 3,
    "random_state": 42
}

# -----------------------------
# 4. Start MLflow run
# -----------------------------
with mlflow.start_run():
    # Log parameters
    mlflow.log_params(params)

    # Train model
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)

    # Predict and calculate metrics
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    # Log metrics
    mlflow.log_metric("accuracy", accuracy)

    # Save model locally and log as artifact
    os.makedirs("outputs", exist_ok=True)
    model_path = "outputs/rf_model.pkl"
    joblib.dump(model, model_path)
    mlflow.log_artifact(model_path, artifact_path="models")

    # Optional: log the model in MLflow's native format
    mlflow.sklearn.log_model(model, artifact_path="sklearn_model")

    print(f"Run finished with accuracy: {accuracy:.4f}")

