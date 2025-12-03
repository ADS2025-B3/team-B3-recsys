import { Link } from 'react-router-dom'
import { useState } from 'react'
import { useSession } from '../context/SessionContext'
import { getUserPreferences } from '../services/preferencesService'
import PreferencesModal from './PreferencesModal'

function Layout({ children }) {
    const { user, isAuthenticated, logout, preferences, setPreferences, token } = useSession()
    const [showPreferencesModal, setShowPreferencesModal] = useState(false)

    const handleLogout = async () => {
        await logout()
    }

    const handlePreferencesClick = () => {
        setShowPreferencesModal(true)
    }

    const handlePreferencesClose = async (saved) => {
        setShowPreferencesModal(false)

        // Refresh preferences if they were saved
        if (saved && token) {
            try {
                const userPrefs = await getUserPreferences(token)
                setPreferences(userPrefs)
            } catch (error) {
                console.error('Error refreshing preferences:', error)
            }
        }
    }

    return (
        <div className="flex flex-col min-h-screen bg-gray-50 dark:bg-gray-900 ">
            <PreferencesModal
                isOpen={showPreferencesModal}
                onClose={handlePreferencesClose}
                existingPreferences={preferences}
                isRequired={false}
            />

            {/* Header */}
            <header className="bg-white dark:bg-gray-800 shadow-sm h-[65px] w-full flex items-center">
                <div className="flex items-center justify-between w-full px-8 py-4">
                    <Link to="/" className="flex items-center space-x-2">
                        <div className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                            🎬 TOP Movie Recommender
                        </div>
                    </Link>

                    {isAuthenticated && (
                        <div className="flex items-center space-x-4">
                            {user && (
                                <span className="text-gray-700 dark:text-gray-300">
                                    Welcome, {user.username || user.name || 'User'}
                                </span>
                            )}
                            <button
                                onClick={handlePreferencesClick}
                                className="px-4 py-2 text-white transition-colors bg-green-600 rounded-md hover:bg-green-700"
                            >
                                ⚙️ Edit Preferences
                            </button>
                            <button
                                onClick={handleLogout}
                                className="px-4 py-2 text-white transition-colors bg-red-600 rounded-md hover:bg-red-700"
                            >
                                Logout
                            </button>
                        </div>
                    )}
                    {!isAuthenticated && (
                        <div>
                            <button
                                onClick={() => { window.location.href = '/login?fromRoute=' + window.location.pathname }}
                                className="px-4 py-2 text-white transition-colors bg-blue-600 rounded-md hover:bg-blue-700"
                            >
                                Login
                            </button>
                        </div>
                    )}
                </div>

            </header>

            {/* Main Content */}
            <main className="container h-[calc(100vh-65px)] max-w-[90%] mx-auto px-4 py-8 ">
                {children}
            </main>

        </div>
    )
}

export default Layout
