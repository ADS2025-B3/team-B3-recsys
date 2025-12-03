import { useState, useCallback } from 'react'
import SearchInput from '../components/SearchInput'
import MovieList from '../components/MovieList'
import { searchMovies } from '../services/movieService'

function SearchPage() {
    const [movies, setMovies] = useState([])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const [hasSearched, setHasSearched] = useState(false)

    const handleSearch = useCallback(async (query) => {
        setLoading(true)
        setError(null)
        setHasSearched(true)

        try {
            const results = await searchMovies(query)
            const moviesParsed = results.map((movie) => ({
                id: movie.id,
                title: movie.title,
                release_year: movie.release_year,
                genres: movie.genres?.split('|') || [],
                average_rating: movie.average_rating,
                rating_count: movie.rating_count
            }))
            setMovies(moviesParsed)
        } catch (err) {
            setError(err.message)
            setMovies([])
        } finally {
            setLoading(false)
        }
    }, [])

    return (
        <div className={`flex flex-col h-full space-y-8 ${hasSearched ? 'justify-start' : 'justify-center'}`}>
            {/* Hero Section */}
            <div className="space-y-4 text-center">
                <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
                    Discover Your Next Favorite Movie
                </h1>
                <p className="text-lg text-gray-600 dark:text-gray-400">
                    Search from thousands of movies and get personalized recommendations
                </p>
            </div>

            {/* Search Section */}
            <div className="py-4">
                <SearchInput onSearch={handleSearch} />
            </div>

            {/* Results Section */}
            <div className="max-w-[90%] w-[90%] mx-auto">
                {hasSearched && (
                    <>
                        {!loading && !error && movies.length > 0 && (
                            <div className="mb-4">
                                <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">
                                    Search Results ({movies.length})
                                </h2>
                            </div>
                        )}
                        <MovieList movies={movies} loading={loading} error={error} />
                    </>
                )}

                {!hasSearched && (
                    <div className="py-12 text-center">
                        <svg
                            className="w-24 h-24 mx-auto text-gray-400"
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
                        <h3 className="mt-4 text-lg font-medium text-gray-900 dark:text-white">
                            Start Your Search
                        </h3>
                        <p className="mt-2 text-gray-500 dark:text-gray-400">
                            Enter a movie title in the search box above to get started
                        </p>
                    </div>
                )}
            </div>
        </div>
    )
}

export default SearchPage
