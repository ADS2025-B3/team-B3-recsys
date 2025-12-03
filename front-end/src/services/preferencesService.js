import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
})

/**
 * Get available genres
 * @returns {Promise<Array<string>>} - List of available genres
 */
export const getAvailableGenres = async () => {
    try {
        const response = await api.get('/movies/genres/')
        return response.data
    } catch (error) {
        console.error('Error fetching genres:', error.response || error)
        throw new Error(error.response?.data?.detail || 'Failed to fetch genres')
    }
}

/**
 * Get user preferences
 * @param {string} token - Authentication token
 * @returns {Promise<Object>} - User preferences
 */
export const getUserPreferences = async (token) => {
    try {
        const response = await api.get('/user_preferences/me', {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        })
        return response.data
    } catch (error) {
        // If 404, user has no preferences yet
        if (error.response?.status === 404) {
            return null
        }
        console.error('Error fetching preferences:', error.response || error)
        throw new Error(error.response?.data?.detail || 'Failed to fetch preferences')
    }
}

/**
 * Save user preferences
 * @param {string} token - Authentication token
 * @param {Array<string>} genres - Selected genre preferences
 * @returns {Promise<Object>} - Updated preferences
 */
export const saveUserPreferences = async (token, genres) => {
    try {
        const response = await api.post(
            '/user_preferences',
            { preferred_genres: genres },
            {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            }
        )
        return response.data
    } catch (error) {
        console.error('Error saving preferences:', error.response || error)
        throw new Error(error.response?.data?.detail || 'Failed to save preferences')
    }
}

/**
 * Update user preferences
 * @param {string} token - Authentication token
 * @param {Array<string>} genres - Selected genre preferences
 * @returns {Promise<Object>} - Updated preferences
 */
export const updateUserPreferences = async (token, genres) => {
    try {
        const response = await api.put(
            '/user_preferences',
            { preferred_genres: genres },
            {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            }
        )
        return response.data
    } catch (error) {
        console.error('Error updating preferences:', error.response || error)
        throw new Error(error.response?.data?.detail || 'Failed to update preferences')
    }
}

export default {
    getAvailableGenres,
    getUserPreferences,
    saveUserPreferences,
    updateUserPreferences,
}
