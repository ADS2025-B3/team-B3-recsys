import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useSession } from '../context/SessionContext'
import { login as loginService } from '../services/authService'
import { getUserPreferences } from '../services/preferencesService'
import PreferencesModal from '../components/PreferencesModal'

function LoginPage() {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)
    const [showPreferences, setShowPreferences] = useState(false)

    const { setToken, setUser, token, setPreferences, setShowPreferencesModal } = useSession()
    const navigate = useNavigate()
    let [searchParams] = useSearchParams();
    useEffect(() => {
        if (loading) return
        if (token) {
            navigate('/')
        }
        return () => { }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [loading])

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError('')
        setLoading(true)

        try {
            const response = await loginService(username, password)
            setToken(response.access_token)
            setUser(response.user)

            // Check for user preferences
            try {
                const userPrefs = await getUserPreferences(response.access_token)
                setPreferences(userPrefs)

                // If no preferences exist, show the modal
                if (!userPrefs) {
                    setShowPreferences(true)
                    setShowPreferencesModal(true)
                } else {
                    // Navigate to the intended page
                    navigateAfterLogin()
                }
            } catch (prefError) {
                console.error('Failed to fetch preferences:', prefError)
                // Show modal if preferences don't exist
                setShowPreferences(true)
                setShowPreferencesModal(true)
            }

        } catch (err) {
            setError(err.message || 'Failed to login')
        } finally {
            setLoading(false)
        }
    }

    const navigateAfterLogin = () => {
        // redirect to previous page if any
        if (history.length > 1) {
            const fromRoute = searchParams.get("fromRoute");
            const base = window.location.origin;
            if (fromRoute) {
                navigate(`${base}${fromRoute}`)
                return
            }
        } else {
            navigate('/')
        }
    }

    const handlePreferencesClose = () => {
        setShowPreferences(false)
        setShowPreferencesModal(false)
        navigateAfterLogin()
    }

    return (
        <div className="flex items-center justify-center flex-1 min-h-full ">
            <PreferencesModal
                isOpen={showPreferences}
                onClose={handlePreferencesClose}
                existingPreferences={null}
                isRequired={true}
            />

            <div className="w-full max-w-md p-8 bg-white rounded-lg shadow-xl bg-opacity-10 backdrop-blur-lg">
                <h1 className="mb-6 text-2xl font-bold text-center text-white">Login</h1>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label htmlFor="username" className="block mb-1 text-sm font-medium text-white">
                            Username
                        </label>
                        <input
                            id="username"
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            disabled={loading}
                        />
                    </div>

                    <div>
                        <label htmlFor="password" className="block mb-1 text-sm font-medium text-white">
                            Password
                        </label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            disabled={loading}
                        />
                    </div>

                    {error && (
                        <div className="p-3 text-sm text-red-600 rounded-md bg-red-50">
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full py-2 text-white transition-colors bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                    >
                        {loading ? 'Logging in...' : 'Login'}
                    </button>
                </form>
            </div>
        </div>
    )
}

export default LoginPage
