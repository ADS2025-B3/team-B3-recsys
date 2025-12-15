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
    const handleOpenPreferences = () => {
        setShowPreferencesModal(true)
    }

    return (
        <div className="flex flex-col min-h-screen bg-gray-900">
            <PreferencesModal
                isOpen={showPreferencesModal}
                onClose={handlePreferencesClose}
                open={handleOpenPreferences}
                existingPreferences={preferences}
                isRequired={false}
            />

            {/* Header */}
            <header className="bg-gray-800 shadow-sm h-[75px] sm:px-8 px-4 py-4 w-full flex items-center">
                <div className="flex items-center justify-between w-full gap-x-3">
                    <Link to="/" className="flex items-center space-x-2">
                        <div className="text-2xl font-bold text-primary-400">
                            🎬 TOP Movie Recommender
                        </div>
                    </Link>
                    {isAuthenticated && (
                        <div className="flex items-center space-x-4">
                            {user && (
                                <span className="text-gray-300">
                                    Welcome, {user.full_name}!
                                </span>
                            )}
                            <button
                                onClick={handlePreferencesClick}
                                className="flex items-center px-4 py-2 text-white transition-colors rounded-md gap-x-2 "
                            >
                                <i>⚙️</i> <p className='hidden sm:block'>Edit Preferences</p>
                            </button>
                            <button
                                onClick={handleLogout}
                            >
                                <svg className='w-6 h-6' viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" transform="matrix(-1, 0, 0, 1, 0, 0)" stroke="#ffffff" strokeWidth="0.00024000000000000003"><g id="SVGRepo_bgCarrier" strokeWidth="0"></g><g id="SVGRepo_tracerCarrier" strokeLinecap="round" strokeLinejoin="round" stroke="#CCCCCC" strokeWidth="0.192"></g><g id="SVGRepo_iconCarrier"> <path d="M12.9999 2C10.2385 2 7.99991 4.23858 7.99991 7C7.99991 7.55228 8.44762 8 8.99991 8C9.55219 8 9.99991 7.55228 9.99991 7C9.99991 5.34315 11.3431 4 12.9999 4H16.9999C18.6568 4 19.9999 5.34315 19.9999 7V17C19.9999 18.6569 18.6568 20 16.9999 20H12.9999C11.3431 20 9.99991 18.6569 9.99991 17C9.99991 16.4477 9.55219 16 8.99991 16C8.44762 16 7.99991 16.4477 7.99991 17C7.99991 19.7614 10.2385 22 12.9999 22H16.9999C19.7613 22 21.9999 19.7614 21.9999 17V7C21.9999 4.23858 19.7613 2 16.9999 2H12.9999Z" fill="#ffffff"></path> <path d="M13.9999 11C14.5522 11 14.9999 11.4477 14.9999 12C14.9999 12.5523 14.5522 13 13.9999 13V11Z" fill="#ffffff"></path> <path d="M5.71783 11C5.80685 10.8902 5.89214 10.7837 5.97282 10.682C6.21831 10.3723 6.42615 10.1004 6.57291 9.90549C6.64636 9.80795 6.70468 9.72946 6.74495 9.67492L6.79152 9.61162L6.804 9.59454L6.80842 9.58848C6.80846 9.58842 6.80892 9.58778 5.99991 9L6.80842 9.58848C7.13304 9.14167 7.0345 8.51561 6.58769 8.19098C6.14091 7.86637 5.51558 7.9654 5.19094 8.41215L5.18812 8.41602L5.17788 8.43002L5.13612 8.48679C5.09918 8.53682 5.04456 8.61033 4.97516 8.7025C4.83623 8.88702 4.63874 9.14542 4.40567 9.43937C3.93443 10.0337 3.33759 10.7481 2.7928 11.2929L2.08569 12L2.7928 12.7071C3.33759 13.2519 3.93443 13.9663 4.40567 14.5606C4.63874 14.8546 4.83623 15.113 4.97516 15.2975C5.04456 15.3897 5.09918 15.4632 5.13612 15.5132L5.17788 15.57L5.18812 15.584L5.19045 15.5872C5.51509 16.0339 6.14091 16.1336 6.58769 15.809C7.0345 15.4844 7.13355 14.859 6.80892 14.4122L5.99991 15C6.80892 14.4122 6.80897 14.4123 6.80892 14.4122L6.804 14.4055L6.79152 14.3884L6.74495 14.3251C6.70468 14.2705 6.64636 14.1921 6.57291 14.0945C6.42615 13.8996 6.21831 13.6277 5.97282 13.318C5.89214 13.2163 5.80685 13.1098 5.71783 13H13.9999V11H5.71783Z" fill="#ffffff"></path> </g></svg>
                            </button>
                        </div>
                    )}
                    {!isAuthenticated && (
                        <div className="flex items-center space-x-4">
                            <button
                                onClick={() => { window.location.href = '/register' }}
                                className="px-4 py-2 text-white transition-colors bg-green-600 rounded-md hover:bg-green-700"
                            >
                                Register
                            </button>
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

            {/* Main Content  */}
            <main className="h-[calc(100vh-75px)] overflow-y-auto max-h-[calc(100vh-75px)] w-full px-8 py-8">
                <div className="h-full ">
                    {children}
                </div>
            </main>

        </div>
    )
}

export default Layout
