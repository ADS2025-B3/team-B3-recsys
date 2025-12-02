import itertools
import mlflow
from train import run_training, load_config # Importamos tu función anterior

# Definimos la rejilla de búsqueda
param_grid = {
    "n_estimators": [50, 100, 200],
    "max_depth": [5, 10, None]
}

def run_grid_search():
    # 1. Cargar config base
    config = load_config()
    
    # 2. Generar todas las combinaciones
    keys, values = zip(*param_grid.items())
    combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]
    
    print(f"Iniciando Grid Search con {len(combinations)} combinaciones...")
    
    # 3. Iterar y entrenar
    for i, params in enumerate(combinations):
        print(f"\n--- Run {i+1}/{len(combinations)}: {params} ---")
        
        # Sobrescribir los parámetros en la configuración cargada en memoria
        config["model"]["params"].update(params)
        
        # Modificar nombre del experimento para identificarlo en MLflow
        run_name = f"rf_grid_{i}_est{params['n_estimators']}_d{params['max_depth']}"
        
        # Lanzamos el entrenamiento pasando el config modificado
        # (Necesitamos modificar ligeramente train.py para aceptar config como argumento, ver abajo)
        run_training(config_override=config, run_name_override=run_name)

if __name__ == "__main__":
    run_grid_search()