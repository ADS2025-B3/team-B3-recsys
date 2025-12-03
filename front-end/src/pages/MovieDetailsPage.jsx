import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getMovieById, rateMovie, getUserRating } from '../services/movieService'
import { useSession } from '../context/SessionContext'
import StarRating from '../components/StarRating'

function MovieDetailsPage() {
    const { id } = useParams()
    const navigate = useNavigate()
    const { isAuthenticated, token, preferences } = useSession()

    const [movie, setMovie] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    // Rating state
    const [userRating, setUserRating] = useState(0)
    const [submittingRating, setSubmittingRating] = useState(false)
    const [ratingSuccess, setRatingSuccess] = useState(false)

    async function fetchMovieDetails() {
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
    async function fetchUserRating() {
        setLoading(true)
        try {
            const rating = await getUserRating(id, token)
            setUserRating(rating.rating || 0)
        } catch (err) {
            setError(err.message)
            console.error('Failed to fetch user rating:', err)
        }
        finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchMovieDetails()
        if (isAuthenticated)
            fetchUserRating()
        else
            setUserRating(0)
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [id, isAuthenticated, token])

    const handleRatingChange = async (rating) => {
        setUserRating(rating)
        setSubmittingRating(true)
        setRatingSuccess(false)

        try {
            const response = await rateMovie(id, rating, token)
            if (response) {
                setRatingSuccess(true)
                fetchUserRating()
                fetchMovieDetails()
            }
            else {
                throw new Error('Failed to submit rating')
            }

        } catch (err) {
            console.error('Failed to submit rating:', err)
        } finally {
            setSubmittingRating(false)
        }
    }

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
        <section className='flex flex-col h-full gap-y-6'>
            {/* Back Button */}
            <button
                onClick={() => navigate('/')}
                className="flex items-center text-primary-400 hover:text-primary-300"
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
            <div className="flex flex-1 bg-white rounded-lg shadow-lg dark:bg-gray-800">
                {/* Poster */}
                {movie.poster_path ? (
                    <img
                        src={movie.poster_path}
                        alt={movie.title}
                        className="object-cover h-full rounded-l-lg aspect-[2/3] "
                    />
                ) : (
                    <div className="flex items-center justify-center h-full rounded-l-lg aspect-[2/3]  bg-gray-300  dark:bg-gray-700">
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
                {/* Details */}
                <div className="p-8 md:w-2/3">
                    <h1 className="mb-4 text-3xl font-bold text-gray-900 dark:text-white">
                        {movie.title}
                    </h1>

                    {/* Rating and Year */}
                    <div className="flex items-center mb-6 space-x-4">
                        {movie.average_rating !== null && movie.average_rating !== undefined && (
                            <div className="flex items-center">
                                <svg
                                    className="w-6 h-6 text-yellow-400"
                                    fill="currentColor"
                                    viewBox="0 0 20 20"
                                >
                                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                </svg>
                                <span className="ml-2 text-xl font-semibold text-gray-900 dark:text-white">
                                    {movie.average_rating.toFixed(1)}
                                </span>
                                <span className="ml-1 text-sm text-gray-500 dark:text-gray-400">
                                    ({movie.rating_count || 0} ratings)
                                </span>
                            </div>
                        )}
                        {movie.release_year && (
                            <span className="text-lg text-gray-600 dark:text-gray-400">
                                {movie.release_year}
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
                                        className={`px-3 py-1 text-sm rounded-full  ${preferences?.preferred_genres.includes(genre) ? 'border-2 border-green-900 bg-green-200 text-green-900' : 'bg-primary-900 text-white '} `}
                                    >
                                        {genre}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}


                    {/* Rating Section */}
                    <div className="p-4 mb-6 rounded-lg bg-gray-50 dark:bg-gray-700">
                        <h3 className="mb-3 text-sm font-semibold text-gray-500 uppercase dark:text-gray-400">
                            Rate This Movie
                        </h3>

                        {!isAuthenticated && (
                            <div className="p-3 mb-3 border border-blue-200 rounded-lg bg-blue-50 dark:bg-blue-900 dark:border-blue-700">
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
                                    <div className="w-4 h-4 mr-2 border-b-2 rounded-full animate-spin border-primary-600"></div>
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
                </div>
            </div>
        </section>
    )
}

export default MovieDetailsPage
