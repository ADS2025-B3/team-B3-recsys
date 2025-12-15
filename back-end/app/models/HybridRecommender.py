import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

class HybridRecommender:
    """
    Hybrid system that combines:
    - SVD Collaborative Filtering (for trained users)
    - Content-Based Filtering with initial ratings
    - Explicit genre preferences
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
        
        # Convert pipe-separated genres to binary columns
        for genre in self.genre_cols:
            self.movies_catalog[genre] = self.movies_catalog['genres'].apply(
                lambda x: 1 if genre in str(x).split('|') else 0
            )
        
        self.movie_features = self.movies_catalog[['movie_id'] + self.genre_cols].set_index('movie_id')
    
    def _build_user_profile_hybrid(self, user_ratings=None, preferred_genres=None, 
                                   genre_weight=0.3, rating_weight=0.7):
        """
        Builds user profile combining ratings AND preferred genres.
        
        :param user_ratings: List of tuples [(movie_id, rating), ...]
        :param preferred_genres: List of strings ['Action', 'Sci-Fi']
        :param genre_weight: Weight of explicit preferences (0-1)
        :param rating_weight: Weight of historical ratings (0-1)
        :return: Combined preference vector
        """
        profile_from_ratings = np.zeros(len(self.genre_cols))
        profile_from_genres = np.zeros(len(self.genre_cols))
        
        # 1. Component: Historical ratings (observed behavior)
        if user_ratings and len(user_ratings) > 0:
            total_weight = 0
            for movie_id, rating in user_ratings:
                if movie_id in self.movie_features.index:
                    movie_vector = self.movie_features.loc[movie_id].values
                    # Weight more the movies with better ratings
                    profile_from_ratings += movie_vector * rating
                    total_weight += rating
            
            if total_weight > 0:
                profile_from_ratings /= total_weight
        
        # 2. Component: Explicit genres (declared preferences)
        if preferred_genres and len(preferred_genres) > 0:
            for i, genre in enumerate(self.genre_cols):
                if genre in preferred_genres:
                    profile_from_genres[i] = 1.0
        
        # 3. Combine both profiles with configurable weights
        has_ratings = np.any(profile_from_ratings > 0)
        has_genres = np.any(profile_from_genres > 0)
        
        if has_ratings and has_genres:
            # We have both signals → combine them
            combined_profile = (rating_weight * profile_from_ratings + 
                               genre_weight * profile_from_genres)
            # Normalize to sum to 1
            combined_profile /= (rating_weight + genre_weight)
            print(f"Using hybrid profile (ratings + genres)")
            
        elif has_ratings:
            # Only ratings
            combined_profile = profile_from_ratings
            print(f"Using ratings-based profile only")
            
        elif has_genres:
            # Only genres
            combined_profile = profile_from_genres
            print(f"Using genre-based profile only")
            
        else:
            # No information
            combined_profile = np.zeros(len(self.genre_cols))
            print(f"No profile information available")
        
        return combined_profile
    
    def recommend_for_new_user(self, user_ratings=None, preferred_genres=None, 
                               n=10, genre_weight=0.3, rating_weight=0.7,
                               exclude_rated=True, diversity_boost=False):
        """
        Recommends movies for a NEW user combining ratings and genres.
        
        :param user_ratings: List of tuples [(movie_id, rating), ...]
        :param preferred_genres: List of strings - favorite genres
        :param n: Number of recommendations
        :param genre_weight: Importance of explicit genres (default 0.3)
        :param rating_weight: Importance of historical ratings (default 0.7)
        :param exclude_rated: If True, excludes already rated movies
        :param diversity_boost: If True, penalizes over-represented genres
        :return: List of movie_ids
        """
        
        # 1. Build hybrid profile
        user_profile = self._build_user_profile_hybrid(
            user_ratings=user_ratings,
            preferred_genres=preferred_genres,
            genre_weight=genre_weight,
            rating_weight=rating_weight
        )
        
        # If no information, use fallback
        if not np.any(user_profile > 0):
            print("No profile info - recommending popular items")
            return self._recommend_popular(n)
        
        # 2. Calculate similarity with ALL movies
        movie_features_matrix = self.movie_features.values
        user_profile_reshaped = user_profile.reshape(1, -1)
        
        similarities = cosine_similarity(user_profile_reshaped, movie_features_matrix).flatten()
        
        # 3. (Optional) Diversity boost: penalize already recommended genres
        if diversity_boost:
            similarities = self._apply_diversity_penalty(similarities, user_profile)
        
        # 4. Sort by similarity
        movie_indices = similarities.argsort()[::-1]
        
        # 5. Filter already rated movies
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
        Penalizes movies from over-represented genres to increase diversity.
        """
        genre_dominance = user_profile / (user_profile.sum() + 1e-10)
        
        # For each movie, calculate how much overlap it has with dominant genres
        movie_features_matrix = self.movie_features.values
        overlap = movie_features_matrix @ genre_dominance
        
        # Penalize similarities of highly overlapped movies
        penalized_similarities = similarities * (1 - penalty_factor * overlap)
        
        return penalized_similarities
    
    def _get_movie_genres(self, movie_id):
        """Returns list of genres for a movie"""
        if movie_id in self.movie_features.index:
            genres = self.movie_features.loc[movie_id]
            return [self.genre_cols[i] for i, val in enumerate(genres) if val == 1]
        return []
    
    def recommend_for_existing_user(self, user_id, n=10):
        """
        Recommends for an EXISTING user in the SVD model.
        """
        return self.svd_model.recommend_top_n(user_id, n=n)
    
    def _recommend_popular(self, n=10):
        """Fallback: most popular/best rated movies."""
        train_df = self.svd_model.train
        
        movie_stats = train_df.groupby('movie_id').agg({
            'rating': ['mean', 'count']
        }).reset_index()
        
        movie_stats.columns = ['movie_id', 'rating_mean', 'rating_count']
        
        # Filter movies with at least 50 ratings
        popular = movie_stats[movie_stats['rating_count'] >= 50]
        
        # Calculate combined score (Bayesian average)
        C = popular['rating_count'].mean()
        m = popular['rating_mean'].mean()
        
        popular['bayesian_avg'] = (
            (popular['rating_count'] / (popular['rating_count'] + C)) * popular['rating_mean'] +
            (C / (popular['rating_count'] + C)) * m
        )
        
        popular = popular.sort_values('bayesian_avg', ascending=False)
        
        return popular['movie_id'].head(n).tolist()
    
    def predict_rating(self, user_id, movie_id, user_ratings=None, preferred_genres=None):
        """
        Predicts the rating a user would give to a specific movie.
        
        :param user_id: User ID
        :param movie_id: Movie ID
        :param user_ratings: List of tuples [(movie_id, rating), ...] (for new users)
        :param preferred_genres: List of strings (for new users)
        :return: Dict with rating prediction (1-5) and confidence level
        """
        
        # Case 1: Existing user in the SVD model
        if user_id in self.svd_model.users_id2index:
            predicted_rating = self.svd_model.predict_score(user_id, movie_id)
            
            # Calculate confidence based on how many ratings the user has
            user_rating_count = len(self.svd_model.train[
                self.svd_model.train.user_id == user_id
            ])
            
            # Normalize confidence (max 100 ratings = confidence 1.0)
            confidence = min(user_rating_count / 100.0, 1.0)
            
            return {
                'predicted_rating': float(np.clip(predicted_rating, 1, 5)),
                'confidence': confidence,
                'method': 'collaborative_filtering'
            }
        
        # Case 2: New user → use content-based
        else:
            return self._predict_rating_content_based(
                movie_id, 
                user_ratings, 
                preferred_genres
            )
    
    def _predict_rating_content_based(self, movie_id, user_ratings=None, preferred_genres=None):
        """
        Predicts rating using content similarity (for new users).
        """
        
        if movie_id not in self.movie_features.index:
            # Movie not found → return average rating
            return {
                'predicted_rating': 3.0,
                'confidence': 0.0,
                'method': 'fallback_mean'
            }
        
        # 1. Build user profile
        user_profile = self._build_user_profile_hybrid(
            user_ratings=user_ratings,
            preferred_genres=preferred_genres
        )
        
        # 2. If no profile, use global average rating of the movie
        if not np.any(user_profile > 0):
            movie_avg = self._get_movie_average_rating(movie_id)
            return {
                'predicted_rating': movie_avg,
                'confidence': 0.1,
                'method': 'movie_average'
            }
        
        # 3. Calculate similarity between user profile and movie
        movie_vector = self.movie_features.loc[movie_id].values.reshape(1, -1)
        user_profile_reshaped = user_profile.reshape(1, -1)
        
        similarity = cosine_similarity(user_profile_reshaped, movie_vector)[0][0]
        
        # 4. Convert similarity (0-1) to rating (1-5)
        # Mapping: similarity 0 = rating 1, similarity 1 = rating 5
        predicted_rating = 1 + (similarity * 4)
        
        # 5. Adjust with movie average rating (regularization)
        movie_avg = self._get_movie_average_rating(movie_id)
        alpha = 0.3  # Weight of movie average
        
        predicted_rating = (1 - alpha) * predicted_rating + alpha * movie_avg
        
        # 6. Calculate confidence based on number of user ratings
        confidence = min(len(user_ratings or []) / 20.0, 0.8) if user_ratings else 0.2
        
        return {
            'predicted_rating': float(np.clip(predicted_rating, 1, 5)),
            'confidence': confidence,
            'similarity_score': float(similarity),
            'method': 'content_based'
        }
    
    def _get_movie_average_rating(self, movie_id):
        """Gets the average rating of a movie from the training dataset."""
        train_df = self.svd_model.train
        
        movie_ratings = train_df[train_df.movie_id == movie_id]['rating']
        
        if len(movie_ratings) > 0:
            return float(movie_ratings.mean())
        else:
            # Fallback: global average rating
            return float(train_df['rating'].mean())
    
    def will_user_like(self, user_id, movie_id, user_ratings=None, 
                      preferred_genres=None, threshold=3.5):
        """
        Determines if the user will like a movie (binary classification).
        
        :param threshold: Minimum rating to consider that they "will like it" (default 3.5)
        :return: Dict with boolean prediction and details
        """
        
        prediction = self.predict_rating(
            user_id, 
            movie_id, 
            user_ratings, 
            preferred_genres
        )
        
        will_like = prediction['predicted_rating'] >= threshold
        
        # Get movie genres for explanation
        movie_genres = self._get_movie_genres(movie_id)
        
        return {
            'will_like': will_like,
            'predicted_rating': prediction['predicted_rating'],
            'confidence': prediction['confidence'],
            'movie_genres': movie_genres,
            'explanation': self._generate_explanation(
                will_like, 
                prediction, 
                movie_genres,
                user_ratings,
                preferred_genres
            )
        }
    
    def _generate_explanation(self, will_like, prediction, movie_genres, 
                             user_ratings, preferred_genres):
        """Generates human-readable explanation of the prediction."""
        
        rating = prediction['predicted_rating']
        confidence = prediction['confidence']
        
        if will_like:
            base_msg = f"✓ You will probably like it (estimated rating: {rating:.1f}/5)"
        else:
            base_msg = f"✗ You probably won't like it (estimated rating: {rating:.1f}/5)"
        
        # Add reasons
        reasons = []
        
        if preferred_genres and movie_genres:
            matching_genres = set(preferred_genres) & set(movie_genres)
            if matching_genres:
                reasons.append(f"Matches your favorite genres: {', '.join(matching_genres)}")
        
        if user_ratings:
            reasons.append(f"Based on your {len(user_ratings)} previous ratings")
        
        if confidence < 0.3:
            reasons.append("⚠️ Low confidence - we need more information about your tastes")
        
        explanation = base_msg
        if reasons:
            explanation += "\n" + "\n".join(f"  • {r}" for r in reasons)
        
        return explanation
    
    def batch_predict_ratings(self, user_id, movie_ids, user_ratings=None, 
                             preferred_genres=None):
        """
        Predicts ratings for multiple movies (efficient).
        
        :param movie_ids: List of movie IDs
        :return: DataFrame with predictions
        """
        predictions = []
        
        for movie_id in movie_ids:
            pred = self.predict_rating(
                user_id, 
                movie_id, 
                user_ratings, 
                preferred_genres
            )
            
            predictions.append({
                'movie_id': movie_id,
                'predicted_rating': pred['predicted_rating'],
                'confidence': pred['confidence'],
                'method': pred['method']
            })
        
        return pd.DataFrame(predictions).sort_values('predicted_rating', ascending=False)
    
    def explain_recommendation(self, movie_id, user_profile):
        """
        Explains why a movie was recommended.
        
        :param movie_id: Recommended movie ID
        :param user_profile: User profile vector
        :return: String with explanation
        """
        if movie_id not in self.movie_features.index:
            return "Movie not found"
        
        movie_vector = self.movie_features.loc[movie_id].values
        movie_genres = self._get_movie_genres(movie_id)
        
        # Calculate contribution of each genre
        genre_contributions = user_profile * movie_vector
        
        # Sort by contribution
        top_genres_idx = genre_contributions.argsort()[::-1][:3]
        top_genres = [self.genre_cols[i] for i in top_genres_idx if genre_contributions[i] > 0]
        
        explanation = f"Recommended because you like: {', '.join(top_genres)}"
        
        return explanation