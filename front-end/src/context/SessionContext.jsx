import { createContext, useContext, useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { logout as logoutService, getCurrentUser } from '../services/authService'

const SessionContext = createContext(null)

export const SessionProvider = ({ children }) => {
    const [token, setToken] = useState(null)
    const [user, setUser] = useState(null)
    const [loading, setLoading] = useState(true)

    const navigate = useNavigate()

    useEffect(() => {
        const initSession = async () => {
            const storedToken = localStorage.getItem('token')
            if (storedToken) {
                setToken(storedToken)
                try {
                    const userData = await getCurrentUser(storedToken)
                    setUser(userData)
                } catch (error) {
                    console.error('Failed to fetch user data:', error)
                    // maybe invalid, clear it
                    localStorage.removeItem('token')
                    setToken(null)
                }
                finally {
                    setLoading(false)
                }
            }
            else {
                setLoading(false)
            }
        }
        initSession()
    }, [navigate])

    useEffect(() => {
        if (token) {
            localStorage.setItem('token', token)
        } else {
            localStorage.removeItem('token')
        }
    }, [token])

    const logout = async () => {
        try {
            if (token) {
                await logoutService(token)
            }
        } finally {
            setToken(null)
            setUser(null)
        }
    }

    const value = {
        token,
        setToken,
        user,
        setUser,
        isAuthenticated: !!token,
        logout,
        loading,
    }

    return (
        <SessionContext.Provider value={value}>
            {
                loading ?
                    <main className=' flex flex-1 min-h-full justify-center items-center text-white '>
                        Loading...
                    </main>
                    :
                    children
            }
        </SessionContext.Provider>
    )
}

export const useSession = () => {
    const context = useContext(SessionContext)
    if (!context) {
        throw new Error('useSession has to be used within a SessionProvider')
    }
    return context
}
