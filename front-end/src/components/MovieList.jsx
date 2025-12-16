import MovieCard from './MovieCard'

function MovieList({ movies, loading, showPredictedRating = false, isAuthenticated }) {
    if (loading) {
        return (
            <div className="flex items-center justify-center py-12">
                <div className="w-12 h-12 border-b-2 rounded-full animate-spin border-primary-600"></div>
            </div>
        )
    }


    if (!movies || movies.length === 0) {
        return (
            <div className="py-12 text-center">
                <svg
                    className="w-12 h-12 mx-auto text-gray-400"
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
                <h3 className="mt-2 text-sm font-medium text-white">No movies found</h3>
                <p className="mt-1 text-sm text-gray-400">
                    Try searching with different keywords
                </p>
            </div>
        )
    }

    return (
        <div className={`grid grid-cols-1 gap-6 overflow-y-auto  ${isAuthenticated ? 'xl:grid-cols-3 lg:grid-cols-2' : 'md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5'}`}>
            {movies.map((movie) => (
                <MovieCard key={movie.id} movie={movie} showPredictedRating={showPredictedRating} />
            ))}
        </div>
    )
}

export default MovieList
