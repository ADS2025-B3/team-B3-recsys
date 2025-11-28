import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
})

/**
 * Login user
 * @param {string} username - Username
 * @param {string} password - Password
 * @returns {Promise<Object>} - Login response with token and user data
 */
export const login = async (username, password) => {
    try {
        const response = await api.post('/auth/login', {
            username,
            password,
        })
        return response.data
    } catch (error) {
        console.error('Error logging in:', error)
        throw new Error(error.response?.data?.message || 'Failed to login')
    }
}

/**
 * Get current user info
 * @param {string} token - Authentication token
 * @returns {Promise<Object>} - User data
 */
export const getCurrentUser = async (token) => {
    try {
        const response = await api.get('/auth/me', {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        })
        return response.data
    } catch (error) {
        console.error('Error fetching user:', error)
        throw new Error(error.response?.data?.message || 'Failed to fetch user')
    }
}

/**
 * Logout user
 * @param {string} token - Authentication token
 * @returns {Promise<void>}
 */
export const logout = async (token) => {
    try {
        await api.post('/auth/logout', {}, {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        })
    } catch (error) {
        console.error('Error logging out:', error)
        // No lanzamos error porque el logout local debe funcionar aunque falle el servidor
    }
}

export default {
    login,
    getCurrentUser,
    logout,
}
