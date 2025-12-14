import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

class HybridRecommender:
    """
    Sistema híbrido que combina:
    - SVD Collaborative Filtering (usuarios entrenados)
    - Content-Based Filtering con ratings iniciales
    - Preferencias explícitas de géneros
    """
    
    def __init__(self, svd_model, movies_catalog_path):
        self.svd_model = svd_model
        self.movies_catalog = pd.read_csv(movies_catalog_path)
        
        self.genre_cols = [
            "unknown", "Action", "Adventure", "Animation", "Children",
            "Comedy", "Crime", "Documentary", "Drama", "Fantasy",
            "Film-Noir", "Horror", "Musical", "Mystery", "Romance",
            "Sci-Fi", "Thriller", "War", "Western"
        ]
        
        self.movie_features = self.movies_catalog[['movie_id'] + self.genre_cols].set_index('movie_id')
    
    def _build_user_profile_hybrid(self, user_ratings=None, preferred_genres=None, 
                                   genre_weight=0.3, rating_weight=0.7):
        """
        Construye perfil combinando ratings Y géneros preferidos.
        
        :param user_ratings: List of tuples [(movie_id, rating), ...]
        :param preferred_genres: List of strings ['Action', 'Sci-Fi']
        :param genre_weight: Peso de las preferencias explícitas (0-1)
        :param rating_weight: Peso de los ratings históricos (0-1)
        :return: Vector combinado de preferencias
        """
        profile_from_ratings = np.zeros(len(self.genre_cols))
        profile_from_genres = np.zeros(len(self.genre_cols))
        
        # 1. Componente: Ratings históricos (comportamiento observado)
        if user_ratings and len(user_ratings) > 0:
            total_weight = 0
            for movie_id, rating in user_ratings:
                if movie_id in self.movie_features.index:
                    movie_vector = self.movie_features.loc[movie_id].values
                    # Ponderamos más las películas con mejor rating
                    profile_from_ratings += movie_vector * rating
                    total_weight += rating
            
            if total_weight > 0:
                profile_from_ratings /= total_weight
        
        # 2. Componente: Géneros explícitos (preferencias declaradas)
        if preferred_genres and len(preferred_genres) > 0:
            for i, genre in enumerate(self.genre_cols):
                if genre in preferred_genres:
                    profile_from_genres[i] = 1.0
        
        # 3. Combinar ambos perfiles con pesos configurables
        has_ratings = np.any(profile_from_ratings > 0)
        has_genres = np.any(profile_from_genres > 0)
        
        if has_ratings and has_genres:
            # Tenemos ambas señales → combinarlas
            combined_profile = (rating_weight * profile_from_ratings + 
                               genre_weight * profile_from_genres)
            # Normalizar para que sume 1
            combined_profile /= (rating_weight + genre_weight)
            print(f"Using hybrid profile (ratings + genres)")
            
        elif has_ratings:
            # Solo ratings
            combined_profile = profile_from_ratings
            print(f"Using ratings-based profile only")
            
        elif has_genres:
            # Solo géneros
            combined_profile = profile_from_genres
            print(f"Using genre-based profile only")
            
        else:
            # Sin información
            combined_profile = np.zeros(len(self.genre_cols))
            print(f"No profile information available")
        
        return combined_profile
    
    def recommend_for_new_user(self, user_ratings=None, preferred_genres=None, 
                               n=10, genre_weight=0.3, rating_weight=0.7,
                               exclude_rated=True, diversity_boost=False):
        """
        Recomienda películas para un usuario NUEVO combinando ratings y géneros.
        
        :param user_ratings: List of tuples [(movie_id, rating), ...]
        :param preferred_genres: List of strings - géneros favoritos
        :param n: Número de recomendaciones
        :param genre_weight: Importancia de géneros explícitos (default 0.3)
        :param rating_weight: Importancia de ratings históricos (default 0.7)
        :param exclude_rated: Si True, excluye películas ya calificadas
        :param diversity_boost: Si True, penaliza géneros sobre-representados
        :return: List of movie_ids
        """
        
        # 1. Construir perfil híbrido
        user_profile = self._build_user_profile_hybrid(
            user_ratings=user_ratings,
            preferred_genres=preferred_genres,
            genre_weight=genre_weight,
            rating_weight=rating_weight
        )
        
        # Si no hay información, usar fallback
        if not np.any(user_profile > 0):
            print("No profile info - recommending popular items")
            return self._recommend_popular(n)
        
        # 2. Calcular similitud con TODAS las películas
        movie_features_matrix = self.movie_features.values
        user_profile_reshaped = user_profile.reshape(1, -1)
        
        similarities = cosine_similarity(user_profile_reshaped, movie_features_matrix).flatten()
        
        # 3. (Opcional) Boost de diversidad: penaliza géneros ya recomendados
        if diversity_boost:
            similarities = self._apply_diversity_penalty(similarities, user_profile)
        
        # 4. Ordenar por similitud
        movie_indices = similarities.argsort()[::-1]
        
        # 5. Filtrar películas ya calificadas
        rated_movie_ids = set([mid for mid, _ in (user_ratings or [])])
        
        recommendations = []
        for idx in movie_indices:
            movie_id = self.movie_features.index[idx]
            
            if exclude_rated and movie_id in rated_movie_ids:
                continue
                
            recommendations.append({
                'movie_id': movie_id,
                'similarity_score': similarities[idx],
                'genres': self._get_movie_genres(movie_id)
            })
            
            if len(recommendations) >= n:
                break
        
        return recommendations
    
    def _apply_diversity_penalty(self, similarities, user_profile, penalty_factor=0.1):
        """
        Penaliza películas de géneros sobre-representados para aumentar diversidad.
        """
        genre_dominance = user_profile / (user_profile.sum() + 1e-10)
        
        # Para cada película, calcular cuánto overlap tiene con géneros dominantes
        movie_features_matrix = self.movie_features.values
        overlap = movie_features_matrix @ genre_dominance
        
        # Penalizar similitudes de películas muy solapadas
        penalized_similarities = similarities * (1 - penalty_factor * overlap)
        
        return penalized_similarities
    
    def _get_movie_genres(self, movie_id):
        """Retorna lista de géneros de una película"""
        if movie_id in self.movie_features.index:
            genres = self.movie_features.loc[movie_id]
            return [self.genre_cols[i] for i, val in enumerate(genres) if val == 1]
        return []
    
    def recommend_for_existing_user(self, user_id, n=10):
        """
        Recomienda para un usuario YA EXISTENTE en el modelo SVD.
        """
        return self.svd_model.recommend_top_n(user_id, n=n)
    
    def _recommend_popular(self, n=10):
        """Fallback: películas más populares/mejor valoradas."""
        train_df = self.svd_model.train
        
        movie_stats = train_df.groupby('movie_id').agg({
            'rating': ['mean', 'count']
        }).reset_index()
        
        movie_stats.columns = ['movie_id', 'rating_mean', 'rating_count']
        
        # Filtrar películas con al menos 50 ratings
        popular = movie_stats[movie_stats['rating_count'] >= 50]
        
        # Calcular score combinado (Bayesian average)
        C = popular['rating_count'].mean()
        m = popular['rating_mean'].mean()
        
        popular['bayesian_avg'] = (
            (popular['rating_count'] / (popular['rating_count'] + C)) * popular['rating_mean'] +
            (C / (popular['rating_count'] + C)) * m
        )
        
        popular = popular.sort_values('bayesian_avg', ascending=False)
        
        return popular['movie_id'].head(n).tolist()
    
    def explain_recommendation(self, movie_id, user_profile):
        """
        Explica por qué se recomendó una película.
        
        :param movie_id: ID de la película recomendada
        :param user_profile: Vector de perfil del usuario
        :return: String con explicación
        """
        if movie_id not in self.movie_features.index:
            return "Movie not found"
        
        movie_vector = self.movie_features.loc[movie_id].values
        movie_genres = self._get_movie_genres(movie_id)
        
        # Calcular contribución de cada género
        genre_contributions = user_profile * movie_vector
        
        # Ordenar por contribución
        top_genres_idx = genre_contributions.argsort()[::-1][:3]
        top_genres = [self.genre_cols[i] for i in top_genres_idx if genre_contributions[i] > 0]
        
        explanation = f"Recommended because you like: {', '.join(top_genres)}"
        
        return explanation