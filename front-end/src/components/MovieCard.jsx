import { useNavigate } from 'react-router-dom'
import { useSession } from '../context/SessionContext'

function MovieCard({ movie, showPredictedRating = false }) {
    const navigate = useNavigate()
    const { preferences } = useSession()

    const handleClick = () => {
        navigate(`/movie/${movie.id}`)
    }
    return (
        <div
            onClick={handleClick}
            className="cursor-pointer card"
        >
            {movie.poster_path ? (
                <img
                    src={movie.poster_path}
                    alt={movie.title}
                    className="object-cover w-full h-64"
                />
            ) : (
                <div className="flex items-center justify-center w-full h-64 bg-gray-700">
                    <svg
                        className="w-16 h-16 text-gray-400"
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
            <div className="p-4">

                <h3 className="text-lg font-semibold text-white truncate">
                    {movie.title}
                </h3>
                <div className="flex items-center mt-1 gap-x-8">

                    {movie.release_year && (
                        <p className="text-sm text-gray-400 ">
                            {movie.release_year}
                        </p>

                    )}
                    {movie.average_rating !== null && movie.average_rating !== undefined && (
                        <div className="flex items-center">
                            <svg
                                className="w-5 h-5 text-yellow-400"
                                fill="currentColor"
                                viewBox="0 0 20 20"
                            >
                                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                            </svg>
                            <span className="ml-1 text-sm font-semibold text-gray-300">
                                {movie.average_rating.toFixed(1)}
                            </span>
                            <span className="ml-1 text-xs text-gray-400">
                                ({movie.rating_count || 0})
                            </span>
                        </div>
                    )}
                </div>

                {showPredictedRating && movie.predicted_rating !== null && movie.predicted_rating !== undefined && (
                    <div className="flex items-center mt-1">
                        {movie.predicted_rating > 3 ? (
                            <span className="text-xs font-medium text-green-300">
                                We think you would like this
                            </span>
                        ) : (
                            <>
                                <svg
                                    className="w-4 h-4 text-blue-400"
                                    fill="currentColor"
                                    viewBox="0 0 20 20"
                                >
                                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                                </svg>
                                <span className="ml-1 text-xs font-medium text-blue-300">
                                    Predicted: {movie.predicted_rating.toFixed(1)}
                                </span>
                            </>
                        )}
                    </div>
                )}
                {movie.genres && movie.genres.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                        {movie.genres.slice(0, 2).map((genre, index) => (
                            <span
                                key={index}
                                className={"text-xs " + (preferences && preferences.preferred_genres.includes(genre) ? "bg-green-200 border-2 border-green-900 text-green-900 " : "bg-primary-900 text-primary-200") + " px-2 py-1 rounded"}
                            >
                                {genre}
                            </span>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}

export default MovieCard
