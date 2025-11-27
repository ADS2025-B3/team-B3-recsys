import { Link } from 'react-router-dom'

function Layout({ children }) {
    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 ">
            {/* Header */}
            <header className="bg-white dark:bg-gray-800 shadow-sm">
                <div className="container mx-auto px-4 py-4">
                    <Link to="/" className="flex items-center space-x-2">
                        <div className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                            🎬 TOP Movie Recommender
                        </div>
                    </Link>
                </div>
            </header>

            {/* Main Content */}
            <main className="container max-w-[90%] mx-auto px-4 py-8 ">
                {children}
            </main>

        </div>
    )
}

export default Layout
