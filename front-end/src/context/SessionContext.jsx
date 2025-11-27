import { createContext, useContext, useState, useEffect } from 'react'

const SessionContext = createContext(null)

export const SessionProvider = ({ children }) => {
    const [token, setToken] = useState(null)
    const [user, setUser] = useState(null)

    useEffect(() => {
        const storedToken = localStorage.getItem('token')
        if (storedToken) setToken(storedToken)
    }, [])

    useEffect(() => {
        if (token) {
            localStorage.setItem('token', token)
        } else {
            localStorage.removeItem('token')
        }
    }, [token])

    const value = {
        token,
        setToken,
        user,
        setUser,
        isAuthenticated: !!token,
    }

    return (
        <SessionContext.Provider value={value}>
            {children}
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
