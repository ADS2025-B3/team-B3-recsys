import { createContext, useContext, useState, useEffect } from 'react'
import { getCurrentUser } from '../services/authService'
import { getUserPreferences } from '../services/preferencesService'

const SessionContext = createContext(null)

export const SessionProvider = ({ children }) => {
    const [token, setToken] = useState(null)
    const [user, setUser] = useState(null)
    const [loading, setLoading] = useState(true)
    const [preferences, setPreferences] = useState(null)
    const [showPreferencesModal, setShowPreferencesModal] = useState(false)

    useEffect(() => {
        const initSession = async () => {
            const storedToken = localStorage.getItem('token')
            if (storedToken && !user) {
                setToken(storedToken)
                try {
                    const userData = await getCurrentUser(storedToken)
                    setUser(userData)

                    // Check for user preferences
                    try {
                        const userPrefs = await getUserPreferences(storedToken)
                        setPreferences(userPrefs)

                        // If no preferences exist, show the modal
                        if (!userPrefs) {
                            setShowPreferencesModal(true)
                        }
                    } catch (prefError) {
                        console.error('Failed to fetch preferences:', prefError)
                        // Show modal if preferences don't exist
                        setShowPreferencesModal(true)
                    }
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
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])

    useEffect(() => {
        if (token) {
            localStorage.setItem('token', token)
        } else {
            localStorage.removeItem('token')
        }
    }, [token])

    const logout = async () => {
        setToken(null)
        setUser(null)
        setPreferences(null)
        setShowPreferencesModal(false)
    }

    const value = {
        token,
        setToken,
        user,
        setUser,
        isAuthenticated: !!token,
        logout,
        loading,
        preferences,
        setPreferences,
        showPreferencesModal,
        setShowPreferencesModal,
    }

    return (
        <SessionContext.Provider value={value}>
            {
                loading ?
                    <main className='flex items-center justify-center flex-1 min-h-full text-white '>
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
