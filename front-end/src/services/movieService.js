import axios from 'axios'

// Configure your API base URL here
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
})

/**
 * Search for movies by query string
 * @param {string} query - The search term
 * @returns {Promise<Array>} - Array of movie objects
 */
export const searchMovies = async (query) => {
    try {
        const response = await api.get('/movies/search', {
            params: { q: query }

        })
        return response.data
    } catch (error) {
        console.error('Error searching movies:', error)
        throw new Error(error.response?.data?.message || 'Failed to search movies')
    }
}

/**
 * Get movie details by ID
 * @param {string|number} id - The movie ID
 * @returns {Promise<Object>} - Movie details object
 */
export const getMovieById = async (id) => {
    try {
        const response = await api.get(`/movies/${id}`)
        return response.data
    } catch (error) {
        console.error('Error fetching movie details:', error)

        throw new Error(error.response?.data?.message || 'Failed to fetch movie details')
    }
}

/**
 * Get movie recommendations based on a movie ID
 * @param {string|number} id - The movie ID
 * @returns {Promise<Array>} - Array of recommended movie objects
 */
export const getMovieRecommendations = async (id) => {
    try {
        const response = await api.get(`/movies/${id}/recommendations`)
        return response.data
    } catch (error) {
        console.error('Error fetching movie recommendations:', error)
        throw new Error(error.response?.data?.message || 'Failed to fetch movie recommendations')
    }
}

/**
 * Submit a rating for a movie
 * @param {string|number} movieId - The movie ID
 * @param {number} rating - The rating value (1-5)
 * @param {string} token - The user's authentication token
 * @returns {Promise<Object>} - Response object with the submitted rating
 */
export const rateMovie = async (movieId, rating, token) => {
    try {
        const payload = {
            movie_id: parseInt(movieId),
            rating: rating
        }

        const response = await api.post('/ratings/', payload, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        })
        return response.data
    } catch (error) {
        console.error('Error rating movie:', error)
        throw new Error(error.response?.data?.detail || 'Failed to submit rating')
    }
}

/**
 * Get all user ratings
 * @param {string} token - The user's authentication token
 * @returns {Promise<Array>} - Array of user rating objects
 */
export const getUserRatings = async (token) => {
    try {
        const response = await api.get('/ratings/me', {
            headers: {
                Authorization: `Bearer ${token}`
            }
        })
        return response.data
    } catch (error) {
        console.error('Error fetching user ratings:', error)
        throw new Error(error.response?.data?.detail || 'Failed to fetch user ratings')
    }
}

/**
 * Get user rating for a specific movie
 * @param {string|number} movieId - The movie ID
 * @param {string} token - The user's authentication token
 * @returns {Promise<Object|null>} - The rating object or null if not rated
 */
export const getUserRating = async (movieId, token) => {
    try {
        const response = await api.get(`/ratings/${movieId}/me`, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        })
        return response.data
    } catch (error) {
        console.error('Error fetching user rating:', error)
        throw new Error(error.response?.data?.detail || 'Failed to fetch user rating')
    }
}

/**
 * Get user-specific movie recommendations
 * @param {string} token - The user's authentication token
 * @returns {Promise<Array>} - Array of recommended movie objects
 */
export const getUserRecommendations = async (token) => {
    try {
        const response = await api.get('/recommendations/user', {
            headers: {
                Authorization: `Bearer ${token}`
            }
        })
        return response.data
    } catch (error) {
        console.error('Error fetching user recommendations:', error)
        throw new Error(error.response?.data?.message || 'Failed to fetch user recommendations')
    }
}

/**
 * Get top 10 global movie recommendations
 * @returns {Promise<Array>} - Array of recommended movie objects
 */
export const getGlobalRecommendations = async () => {
    try {
        const response = await api.get('/recommendations/global')
        return response.data
    } catch (error) {
        console.error('Error fetching global recommendations:', error)
        throw new Error(error.response?.data?.message || 'Failed to fetch global recommendations')
    }
}

/**
 * Get predicted rating for a movie
 * @param {string|number} movieId - The movie ID
 * @param {string} token - The user's authentication token
 * @returns {Promise<Object>} - Object with predicted rating
 */
export const getPredictedRating = async (movieId, token) => {
    try {
        const response = await api.get(`/movies/${movieId}/predict`, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        })
        return response.data
    } catch (error) {
        console.error('Error fetching predicted rating:', error)
        throw new Error(error.response?.data?.message || 'Failed to fetch predicted rating')
    }
}

export default {
    searchMovies,
    getMovieById,
    getMovieRecommendations,
    rateMovie,
    getUserRating,
    getUserRatings,
    getUserRecommendations,
    getGlobalRecommendations,
    getPredictedRating,
}