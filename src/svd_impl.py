import numpy as np
import pandas as pd
from scipy.linalg import sqrtm

class SVDCF:
    """
    Collaborative Filtering using Singular Value Decomposition (SVD).
    Adapted from class RecSys_mf.
    """
    
    def __init__(self, num_components=10):
        """
        Constructor.
        :param num_components: Number of latent factors (k) to keep from SVD.
        """
        self.num_components = num_components
        self.train = None
        self.urm = None # User Rating Matrix
        self.Y_hat = None # Reconstructed Matrix (Predictions)
        # Mappings
        self.users_id2index = {}
        self.users_index2id = {}
        self.movies_id2index = {}
        self.movies_index2id = {}
        
    def fit(self, df_train):
        """
        Decomposes the User-Rating Matrix into submatrices.
        :param df_train: Pandas DataFrame with columns ['user_id', 'movie_id', 'rating']
        """
        self.train = df_train
        
        # Create Pivot Table (User-Item Matrix)
        # Note: In production, sparse matrices are better, but we stick to the notebook approach for now
        self.urm = pd.pivot_table(
            df_train[['user_id', 'movie_id', 'rating']],
            columns='movie_id', 
            index='user_id', 
            values='rating'
        )
        
        # Create mappings between internal Matrix Indices and real IDs
        user_index = np.arange(len(self.urm.index))
        self.users_id2index = dict(zip(self.urm.index, user_index))
        self.users_index2id = dict(zip(user_index, self.urm.index))
        
        movie_index = np.arange(len(self.urm.columns))
        self.movies_id2index = dict(zip(self.urm.columns, movie_index))
        self.movies_index2id = dict(zip(movie_index, self.urm.columns))
        
        # Handle NaN values (missing ratings)
        train_matrix = np.array(self.urm)
        mask = np.isnan(train_matrix)
        masked_arr = np.ma.masked_array(train_matrix, mask)
        
        # Compute item means to center the data
        item_means = np.mean(masked_arr, axis=0)
        
        # Fill NaNs with 0 for SVD computation (common baseline approach)
        train_matrix = masked_arr.filled(0)
        
        # Center the matrix (subtract mean)
        x = np.tile(item_means, (train_matrix.shape[0], 1))
        train_matrix = train_matrix - x
        
        # --- THE MATH (SVD) ---
        # Decompose matrix into U, S, V
        U, s, V = np.linalg.svd(train_matrix, full_matrices=False)
        
        # Keep only top k components
        S = np.diag(s[0:self.num_components])
        U = U[:, 0:self.num_components]
        V = V[0:self.num_components, :]
        
        # Reconstruct the matrix (prediction)
        S_root = sqrtm(S)
        USk = np.dot(U, S_root)
        SkV = np.dot(S_root, V)
        
        # Add the means back
        self.Y_hat = np.dot(USk, SkV) + x
        print(f"SVD Fit Complete. Reconstructed Matrix Shape: {self.Y_hat.shape}")

    def predict_score(self, user_id, movie_id):
        """ Returns the predicted rating for a specific user and movie. """
        if movie_id in self.movies_id2index and user_id in self.users_id2index:
            user_idx = self.users_id2index[user_id]
            movie_idx = self.movies_id2index[movie_id]
            return self.Y_hat[user_idx, movie_idx]
        else:
            return 0 # Cold start or unknown item

    def recommend_top_n(self, user_id, n=5):
        """
        Returns top N movie recommendations for a user.
        Excludes movies the user has already seen (in training set).
        """
        if user_id not in self.users_id2index:
            return []
            
        # 1. Get all movie IDs the user has already rated
        seen_items = self.train[self.train.user_id == user_id].movie_id.values
        
        # 2. Identify indices of ALL movies
        all_movie_indices = np.arange(self.Y_hat.shape[1])
        
        # 3. Get the user's row from the predicted matrix
        user_idx = self.users_id2index[user_id]
        user_predictions = self.Y_hat[user_idx, :]
        
        # 4. Filter predictions
        recommendations = []
        for movie_idx in all_movie_indices:
            movie_id = self.movies_index2id[movie_idx]
            
            # Only recommend if not seen
            if movie_id not in seen_items:
                score = user_predictions[movie_idx]
                recommendations.append((movie_id, score))
        
        # 5. Sort by score descending and take top N
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        # Return only the movie_ids
        return [rec[0] for rec in recommendations[:n]]