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
 * Get movie recommendations
 * @param {string|number} id - The movie ID
 * @returns {Promise<Array>} - Array of recommended movie objects
 */
// export const getMovieRecommendations = async (id) => {
//     try {
//         const response = await api.get(`/movies/${id}/recommendations`)
//         return response.data
//     } catch (error) {
//         console.error('Error fetching recommendations:', error)
//         throw new Error(error.response?.data?.message || 'Failed to fetch recommendations')
//     }
// }

export default {
    searchMovies,
    getMovieById,
}
