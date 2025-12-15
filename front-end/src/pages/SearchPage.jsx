import { useState, useCallback, useEffect } from 'react'
import SearchInput from '../components/SearchInput'
import MovieList from '../components/MovieList'
import { searchMovies, getUserRecommendations, getGlobalRecommendations } from '../services/movieService'
import { useSession } from '../context/SessionContext'

function SearchPage() {
    const { isAuthenticated, token } = useSession()
    const [movies, setMovies] = useState([])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const [hasSearched, setHasSearched] = useState(false)
    const [userRecommendations, setUserRecommendations] = useState([])
    const [globalRecommendations, setGlobalRecommendations] = useState([])
    const [loadingRecs, setLoadingRecs] = useState(false)

    useEffect(() => {
        const fetchRecommendations = async () => {
            setLoadingRecs(true)

            // Fetch global recommendations
            try {
                const globalResults = await getGlobalRecommendations()
                const globalParsed = globalResults.map((movie) => ({
                    id: movie.id,
                    title: movie.title,
                    release_year: movie.release_year,
                    genres: movie.genres?.split('|') || [],
                    average_rating: movie.average_rating,
                    rating_count: movie.rating_count
                }))
                setGlobalRecommendations(globalParsed)
            } catch (err) {
                setGlobalRecommendations([])
            }

            // Fetch user recommendations if authenticated
            if (isAuthenticated && token) {
                try {
                    const userResults = await getUserRecommendations(token)
                    const userParsed = userResults.map((movie) => ({
                        id: movie.id,
                        title: movie.title,
                        release_year: movie.release_year,
                        genres: movie.genres?.split('|') || [],
                        average_rating: movie.average_rating,
                        rating_count: movie.rating_count
                    }))
                    setUserRecommendations(userParsed)
                } catch (err) {
                    setUserRecommendations([])
                }
            }

            setLoadingRecs(false)
        }

        fetchRecommendations()
    }, [isAuthenticated, token])

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
        <div className={`flex flex-col h-full space-y-8 
        ${hasSearched || userRecommendations.length > 0 || globalRecommendations.length > 0 ? 'justify-start' : 'justify-center'}`}>
            {/* Hero Section */}
            <div className="space-y-4 text-center">
                <h1 className="text-4xl font-bold text-white">
                    Discover Your Next Favorite Movie
                </h1>
                <p className="text-lg text-gray-400">
                    Search from thousands of movies and get personalized recommendations
                </p>
            </div>

            {/* Search Section */}
            <div className="py-4">
                <SearchInput onSearch={handleSearch} />
            </div>

            {/* Results Section */}
            <div className="max-w-[90%] w-[90%] mx-auto pb-8">
                {hasSearched && (
                    <>
                        {!loading && !error && movies.length > 0 && (
                            <div className="mb-4">
                                <h2 className="text-2xl font-semibold text-white">
                                    Search Results ({movies.length})
                                </h2>
                            </div>
                        )}
                        <MovieList movies={movies} loading={loading} error={error} />
                    </>
                )}

                {!hasSearched && (
                    <>
                        {/* User Recommendations Section */}
                        {isAuthenticated && userRecommendations.length > 0 && (
                            <div className="pb-8">
                                <h2 className="mb-4 text-2xl font-semibold text-white">
                                    Recommended for You
                                </h2>
                                <MovieList movies={userRecommendations} loading={loadingRecs} />
                            </div>
                        )}

                        {/* Global Recommendations Section */}
                        {globalRecommendations.length > 0 &&
                            <div className="pb-8">
                                <h2 className="mb-4 text-2xl font-semibold text-white">
                                    Top 10 Global Recommendations
                                </h2>
                                <MovieList movies={globalRecommendations} loading={loadingRecs} />
                            </div>}
                    </>
                )}
            </div>
        </div>
    )
}

export default SearchPage
