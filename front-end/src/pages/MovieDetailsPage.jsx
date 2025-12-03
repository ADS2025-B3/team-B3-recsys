import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getMovieById } from '../services/movieService'

function MovieDetailsPage() {
    const { id } = useParams()
    const navigate = useNavigate()
    const [movie, setMovie] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        const fetchMovieDetails = async () => {
            setLoading(true)
            setError(null)

            try {
                const movieData = await getMovieById(id)
                const movieParsed = {
                    ...movieData,
                    genres: movieData.genres?.split('|') || []
                }
                setMovie(movieParsed)
            } catch (err) {
                setError(err.message)
            } finally {
                setLoading(false)
            }
        }

        fetchMovieDetails()
    }, [id])

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="w-16 h-16 border-b-2 rounded-full animate-spin border-primary-600"></div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="max-w-2xl mx-auto mt-8">
                <div className="relative px-4 py-3 text-red-700 bg-red-100 border border-red-400 rounded dark:bg-red-900 dark:border-red-700 dark:text-red-200">
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
            <div className="py-12 text-center">
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
            <div className="overflow-hidden bg-white rounded-lg shadow-lg dark:bg-gray-800">
                <div className="md:flex">
                    {/* Poster */}
                    <div className="md:w-1/3">
                        {movie.poster_path ? (
                            <img
                                src={movie.poster_path}
                                alt={movie.title}
                                className="object-cover w-full h-full"
                            />
                        ) : (
                            <div className="flex items-center justify-center w-full bg-gray-300 h-96 dark:bg-gray-700">
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
                    <div className="p-8 md:w-2/3">
                        <h1 className="mb-4 text-3xl font-bold text-gray-900 dark:text-white">
                            {movie.title}
                        </h1>

                        {/* Rating and Year */}
                        <div className="flex items-center mb-6 space-x-4">
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
                                <h3 className="mb-2 text-sm font-semibold text-gray-500 uppercase dark:text-gray-400">
                                    Genres
                                </h3>
                                <div className="flex flex-wrap gap-2">
                                    {movie.genres.map((genre, index) => (
                                        <span
                                            key={index}
                                            className="px-3 py-1 text-sm rounded-full bg-primary-100 dark:bg-primary-900 text-primary-800 dark:text-primary-200"
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
                                <h3 className="mb-2 text-sm font-semibold text-gray-500 uppercase dark:text-gray-400">
                                    Overview
                                </h3>
                                <p className="leading-relaxed text-gray-700 dark:text-gray-300">
                                    {movie.overview}
                                </p>
                            </div>
                        )}

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
