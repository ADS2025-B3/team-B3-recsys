import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import SearchPage from './pages/SearchPage'
import MovieDetailsPage from './pages/MovieDetailsPage'
import NotFound from './pages/NotFound'
import LoginPage from './pages/LoginPage'
import { SessionProvider } from './context/SessionContext'

function App() {
    return (
        <SessionProvider>
            <Layout>
                <Routes>
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/" element={<SearchPage />} />
                    <Route path="/movie/:id" element={<MovieDetailsPage />} />
                    <Route path="*" element={<NotFound />} />
                </Routes>
            </Layout>
        </SessionProvider>
    )
}

export default App
