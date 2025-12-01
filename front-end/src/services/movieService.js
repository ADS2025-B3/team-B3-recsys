import axios from 'axios'

// Configure your API base URL here
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
})

/**
 * Search for movies by query string
 * @param {string} query - The search term
 * @returns {Promise<Array>} - Array of movie objects
 */
export const searchMovies = async (query) => {
    try {
        const response = await api.get('/movies/search', {
            params: { q: query }

        })
        return response.data
    } catch (error) {
        console.error('Error searching movies:', error)
        //mock up data
        return [{
            id: 1,
            title: "Mock Movie 1",
            year: 2022,
            poster_path: "https://proassetspdlcom.cdnstatics2.com/usuaris/libros/fotos/303/original/portada_vengadores-endgame-el-libro-de-la-pelicula_marvel_201910081425.jpg"
        },
        {
            id: 2,
            title: "Mock Movie 2",
            year: 2021,
            poster_path: "https://m.media-amazon.com/images/I/81ExhpBEbHL._AC_SY679_.jpg"
        },
        {
            id: 3,
            title: "Mock Movie 3",
            year: 2020,
            poster_path: "https://m.media-amazon.com/images/I/51oD6C1XQDL._AC_SY445_.jpg"
        }
        ]
        //throw new Error(error.response?.data?.message || 'Failed to search movies')
    }
}

/**
 * Get movie details by ID
 * @param {string|number} id - The movie ID
 * @returns {Promise<Object>} - Movie details object
 */
export const getMovieById = async (id) => {
    try {
        const response = await api.get(`/movies/${id}`)
        return response.data
    } catch (error) {
        console.error('Error fetching movie details:', error)
        //mock up data
        return {
            id: id,
            title: "Mock Movie Detail",
            overview: "This is a mock description of the movie.",
            release_date: "2022-01-01",
            rating: 8.5,
            genres: ["Action", "Adventure"],
            poster_path: "https://m.media-amazon.com/images/I/81ExhpBEbHL._AC_SY679_.jpg",
            runtime: 130,
            language: "English",
            budget: 200000000,
            revenue: 800000000,

        }
        //throw new Error(error.response?.data?.message || 'Failed to fetch movie details')
    }
}

/**
 * Get movie recommendations
 * @param {string|number} id - The movie ID
 * @returns {Promise<Array>} - Array of recommended movie objects
 */
// export const getMovieRecommendations = async (id) => {
//     try {
//         const response = await api.get(`/movies/${id}/recommendations`)
//         return response.data
//     } catch (error) {
//         console.error('Error fetching recommendations:', error)
//         throw new Error(error.response?.data?.message || 'Failed to fetch recommendations')
//     }
// }

export default {
    searchMovies,
    getMovieById,
}
