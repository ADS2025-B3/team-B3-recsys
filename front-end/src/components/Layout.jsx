import { Link } from 'react-router-dom'
import { useSession } from '../context/SessionContext'

function Layout({ children }) {
    const { user, isAuthenticated, logout } = useSession()

    const handleLogout = async () => {
        await logout()
    }

    return (
        <div className="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900 ">
            {/* Header */}
            <header className="bg-white dark:bg-gray-800 shadow-sm h-[65px] w-full flex items-center">
                <div className="py-4 px-8 flex items-center justify-between w-full">
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
                                onClick={handleLogout}
                                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                            >
                                Logout
                            </button>
                        </div>
                    )}
                    {!isAuthenticated && (
                        <div>
                            <button
                                onClick={() => { window.location.href = '/login' }}
                                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
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
