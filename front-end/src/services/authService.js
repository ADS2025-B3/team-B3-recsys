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
        // OAuth2PasswordRequestForm requires form-data format
        const formData = new URLSearchParams()
        formData.append('username', username)
        formData.append('password', password)

        const response = await api.post('/auth/login', formData, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        })
        const data = response.data.access_token
        if (data) {
            const user = await getCurrentUser(data)
            return { access_token: data, user }
        }
        throw new Error('No access token received')
    } catch (error) {
        console.error('Error logging in:', error.response || error)
        throw new Error(error.response?.data?.detail || 'Failed to login')
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
        console.error('Error fetching user:', error.response || error)
        throw new Error(error.response?.data?.detail || 'Failed to fetch user')
    }
}

export default {
    login,
    getCurrentUser,
}
