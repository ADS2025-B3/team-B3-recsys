import numpy as np
from tqdm import tqdm

def compute_rmse(y_pred, y_true):
    """ Compute Root Mean Squared Error. """
    return np.sqrt(np.mean(np.power(y_pred - y_true, 2)))

def precision(recommended_items, relevant_items):
    is_relevant = np.in1d(recommended_items, relevant_items, assume_unique=True)
    if len(is_relevant) == 0: return 0.0
    precision_score = np.sum(is_relevant, dtype=np.float32) / len(is_relevant)
    return precision_score

def recall(recommended_items, relevant_items):
    if len(relevant_items) == 0: return 0.0
    is_relevant = np.in1d(recommended_items, relevant_items, assume_unique=True)
    recall_score = np.sum(is_relevant, dtype=np.float32) / relevant_items.shape[0]
    return recall_score

def AP(recommended_items, relevant_items):
    if len(relevant_items) == 0: return 0.0
    is_relevant = np.in1d(recommended_items, relevant_items, assume_unique=True)
    # Cumulative sum: precision at 1, at 2, at 3 ...
    p_at_k = is_relevant * np.cumsum(is_relevant, dtype=np.float32) / (1 + np.arange(is_relevant.shape[0]))
    ap_score = np.sum(p_at_k) / np.min([relevant_items.shape[0], is_relevant.shape[0]])
    return ap_score

def evaluate_rmse(estimate_f, data_train, data_test):
    """ RMSE-based predictive performance evaluation with pandas. """
    # Optimizacion: Creamos un set de usuarios conocidos para búsqueda O(1)
    train_users = set(data_train.user_id.unique())
    
    ids_to_estimate = zip(data_test.user_id, data_test.movie_id)
    
    # Si el usuario es conocido, predecimos. Si es nuevo (Cold Start), devolvemos 3 (media)
    estimated = np.array([
        estimate_f(u, i) if u in train_users else 3 
        for (u, i) in ids_to_estimate
    ])
    
    real = data_test.rating.values
    return compute_rmse(estimated, real)

def evaluate_algorithm_top(test_df, recommender_object, at=25, thr_relevant=4):
    """Evalúa Precision, Recall y MAP para el Top N"""
    cumulative_precision = 0.0
    cumulative_recall = 0.0
    cumulative_AP = 0.0
    num_eval = 0

    users = test_df.user_id.unique()
    print(f"Evaluando ranking para {len(users)} usuarios...")

    for user_id in tqdm(users):
        # Items que al usuario le gustaron de verdad (en el set de test)
        relevant_items = test_df[(test_df.user_id == user_id) & (test_df.rating >= thr_relevant)].movie_id.values
        
        if len(relevant_items) > 0:
            # LLAMADA CLAVE: Usamos el método de tu clase SVD
            recommended_items = recommender_object.recommend_top_n(user_id, n=at)
            
            if len(recommended_items) > 0:
                num_eval += 1
                cumulative_precision += precision(recommended_items, relevant_items)
                cumulative_recall += recall(recommended_items, relevant_items)
                cumulative_AP += AP(recommended_items, relevant_items)
            
    if num_eval == 0:
        return {"precision": 0, "recall": 0, "map": 0}

    # Devolvemos un diccionario listo para MLflow
    return {
        "precision": cumulative_precision / num_eval,
        "recall": cumulative_recall / num_eval,
        "map": cumulative_AP / num_eval
    }