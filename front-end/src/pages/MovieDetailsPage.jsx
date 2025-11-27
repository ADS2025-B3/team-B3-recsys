import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getMovieById, rateMovie } from '../services/movieService'
import StarRating from '../components/StarRating'

function MovieDetailsPage() {
    const { id } = useParams()
    const navigate = useNavigate()
    const [movie, setMovie] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    // Mock authentication state - replace with actual auth context later
    const [isAuthenticated, setIsAuthenticated] = useState(false)

    // Rating state
    const [userRating, setUserRating] = useState(0)
    const [submittingRating, setSubmittingRating] = useState(false)
    const [ratingSuccess, setRatingSuccess] = useState(false)

    useEffect(() => {
        const fetchMovieDetails = async () => {
            setLoading(true)
            setError(null)

            try {
                const movieData = await getMovieById(id)
                setMovie(movieData)
            } catch (err) {
                setError(err.message)
            } finally {
                setLoading(false)
            }
        }

        fetchMovieDetails()
    }, [id])

    const handleRatingChange = async (rating) => {
        setUserRating(rating)
        setSubmittingRating(true)
        setRatingSuccess(false)

        try {
            await rateMovie(id, rating)
            setRatingSuccess(true)
            // Hide success message after 3 seconds
            setTimeout(() => setRatingSuccess(false), 3000)
        } catch (err) {
            console.error('Failed to submit rating:', err)
            // Even if it fails, we keep the rating displayed in the UI
        } finally {
            setSubmittingRating(false)
        }
    }

    const toggleAuth = () => {
        setIsAuthenticated(!isAuthenticated)
        if (isAuthenticated) {
            // Clear rating when logging out
            setUserRating(0)
            setRatingSuccess(false)
        }
    }

    if (loading) {
        return (
            <div className="flex justify-center items-center min-h-screen">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600"></div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="max-w-2xl mx-auto mt-8">
                <div className="bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-200 px-4 py-3 rounded relative">
                    <strong className="font-bold">Error!</strong>
                    <span className="block sm:inline"> {error}</span>
                </div>
                <button
                    onClick={() => navigate('/')}
                    className="mt-4 btn-primary"
                >
                    Back to Search
                </button>
            </div>
        )
    }

    if (!movie) {
        return (
            <div className="text-center py-12">
                <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">Movie not found</h2>
                <button
                    onClick={() => navigate('/')}
                    className="mt-4 btn-primary"
                >
                    Back to Search
                </button>
            </div>
        )
    }

    return (
        <div className="space-y-8">
            {/* Mock Auth Toggle - For Development Only */}
            <div className="flex justify-end">
                <button
                    onClick={toggleAuth}
                    className={`px-4 py-2 rounded-lg font-semibold transition-colors ${isAuthenticated
                        ? 'bg-red-600 hover:bg-red-700 text-white'
                        : 'bg-green-600 hover:bg-green-700 text-white'
                        }`}
                >
                    {isAuthenticated ? '🔓 Mock Logout' : '🔒 Mock Login'}
                </button>
            </div>

            {/* Back Button */}
            <button
                onClick={() => navigate('/')}
                className="flex items-center text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300"
            >
                <svg
                    className="w-5 h-5 mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M10 19l-7-7m0 0l7-7m-7 7h18"
                    />
                </svg>
                Back to Search
            </button>

            {/* Movie Details */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
                <div className="md:flex">
                    {/* Poster */}
                    <div className="md:w-1/3">
                        {movie.poster_path ? (
                            <img
                                src={movie.poster_path}
                                alt={movie.title}
                                className="w-full h-full object-cover"
                            />
                        ) : (
                            <div className="w-full h-96 bg-gray-300 dark:bg-gray-700 flex items-center justify-center">
                                <svg
                                    className="w-24 h-24 text-gray-400"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z"
                                    />
                                </svg>
                            </div>
                        )}
                    </div>

                    {/* Details */}
                    <div className="md:w-2/3 p-8">
                        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
                            {movie.title}
                        </h1>

                        {/* Rating and Year */}
                        <div className="flex items-center space-x-4 mb-6">
                            {movie.rating !== undefined && (
                                <div className="flex items-center">
                                    <svg
                                        className="w-6 h-6 text-yellow-400"
                                        fill="currentColor"
                                        viewBox="0 0 20 20"
                                    >
                                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                    </svg>
                                    <span className="ml-2 text-xl font-semibold text-gray-900 dark:text-white">
                                        {movie.rating.toFixed(1)}
                                    </span>
                                </div>
                            )}
                            {movie.release_date && (
                                <span className="text-lg text-gray-600 dark:text-gray-400">
                                    {new Date(movie.release_date).getFullYear()}
                                </span>
                            )}
                        </div>

                        {/* Genres */}
                        {movie.genres && movie.genres.length > 0 && (
                            <div className="mb-6">
                                <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase mb-2">
                                    Genres
                                </h3>
                                <div className="flex flex-wrap gap-2">
                                    {movie.genres.map((genre, index) => (
                                        <span
                                            key={index}
                                            className="bg-primary-100 dark:bg-primary-900 text-primary-800 dark:text-primary-200 px-3 py-1 rounded-full text-sm"
                                        >
                                            {genre}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Overview */}
                        {movie.overview && (
                            <div className="mb-6">
                                <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase mb-2">
                                    Overview
                                </h3>
                                <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                                    {movie.overview}
                                </p>
                            </div>
                        )}

                        {/* Rating Section */}
                        <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                            <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase mb-3">
                                Rate This Movie
                            </h3>

                            {!isAuthenticated && (
                                <div className="mb-3 p-3 bg-blue-50 dark:bg-blue-900 border border-blue-200 dark:border-blue-700 rounded-lg">
                                    <p className="text-sm text-blue-800 dark:text-blue-200">
                                        🔒 Please log in to rate this movie
                                    </p>
                                </div>
                            )}

                            <div className="flex items-center space-x-4">
                                <StarRating
                                    value={userRating}
                                    onChange={handleRatingChange}
                                    disabled={!isAuthenticated || submittingRating}
                                />

                                {submittingRating && (
                                    <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600 mr-2"></div>
                                        Submitting...
                                    </div>
                                )}

                                {ratingSuccess && !submittingRating && (
                                    <div className="flex items-center text-sm text-green-600 dark:text-green-400">
                                        <svg className="w-5 h-5 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                        </svg>
                                        Rating submitted!
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Additional Info */}
                        <div className="grid grid-cols-2 gap-4 text-sm">
                            {movie.runtime && (
                                <div>
                                    <span className="font-semibold text-gray-500 dark:text-gray-400">Runtime:</span>
                                    <span className="ml-2 text-gray-700 dark:text-gray-300">{movie.runtime} min</span>
                                </div>
                            )}
                            {movie.language && (
                                <div>
                                    <span className="font-semibold text-gray-500 dark:text-gray-400">Language:</span>
                                    <span className="ml-2 text-gray-700 dark:text-gray-300">{movie.language}</span>
                                </div>
                            )}
                            {movie.budget && (
                                <div>
                                    <span className="font-semibold text-gray-500 dark:text-gray-400">Budget:</span>
                                    <span className="ml-2 text-gray-700 dark:text-gray-300">
                                        ${movie.budget.toLocaleString()}
                                    </span>
                                </div>
                            )}
                            {movie.revenue && (
                                <div>
                                    <span className="font-semibold text-gray-500 dark:text-gray-400">Revenue:</span>
                                    <span className="ml-2 text-gray-700 dark:text-gray-300">
                                        ${movie.revenue.toLocaleString()}
                                    </span>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default MovieDetailsPage
