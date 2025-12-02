import pandas as pd
import yaml
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
import os

# 1. Cargar configuración
def load_config(config_path="configs/params.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def run_training(config_override=None, run_name_override=None):
    config = config_override if config_override else load_config()
    
    # Configurar MLflow (Task 3.1.6)
    mlflow.set_tracking_uri(config["main"]["tracking_uri"])
    mlflow.set_experiment(config["main"]["project_name"])
    
    print(f"Iniciando run en: {config['main']['tracking_uri']}")

    # Iniciar el run de MLflow
    run_name = run_name_override if run_name_override else config["main"]["experiment_name"]
    with mlflow.start_run(run_name=run_name):
        
        # 2. Cargar datos (usamos los que generaste en la tarea anterior)
        print("Cargando datos...")
        train_df = pd.read_csv(config["data"]["train_path"])
        test_df = pd.read_csv(config["data"]["test_path"])
        
        # Separar Features (X) y Target (y)
        # Asumimos que 'rating' es lo que queremos predecir
        X_train = train_df.drop(["rating", "timestamp"], axis=1)
        y_train = train_df["rating"]
        
        X_test = test_df.drop(["rating", "timestamp"], axis=1)
        y_test = test_df["rating"]

        # 3. Loguear parámetros en MLflow
        params = config["model"]["params"]
        mlflow.log_params(params)
        mlflow.log_param("random_seed", config["main"]["random_seed"])

        # 4. Entrenar Modelo (Task 3.1.9 placeholder - Baseline)
        print(f"Entrenando {config['model']['type']}...")
        model = RandomForestClassifier(
            n_estimators=params["n_estimators"],
            max_depth=params["max_depth"],
            criterion=params["criterion"],
            random_state=config["main"]["random_seed"]
        )
        model.fit(X_train, y_train)

        # 5. Evaluar
        predictions = model.predict(X_test)
        acc = accuracy_score(y_test, predictions)
        f1 = f1_score(y_test, predictions, average='weighted')
        
        print(f"Accuracy: {acc:.4f} | F1 Score: {f1:.4f}")

        # 6. Loguear Métricas y Modelo
        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("f1_score", f1)
        
        # Guardar el modelo en el registro de artefactos de MLflow
        mlflow.sklearn.log_model(model, "model")
        
        # Guardar el archivo de config como evidencia
        mlflow.log_artifact("configs/params.yaml")

if __name__ == "__main__":
    run_training()