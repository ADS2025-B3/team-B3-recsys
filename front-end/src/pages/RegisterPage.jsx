import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { register as registerService } from '../services/authService'
import { useSession } from '../context/SessionContext'

function RegisterPage() {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const [fullName, setFullName] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)
    const [success, setSuccess] = useState(false)
    const { isAuthenticated } = useSession()

    const navigate = useNavigate()

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError('')
        setSuccess(false)

        if (password !== confirmPassword) {
            setError('Passwords do not match')
            return
        }

        if (password.length < 8) {
            setError('Password must be at least 8 characters long')
            return
        }
        setLoading(true)
        try {
            await registerService(email, password, fullName)
            setSuccess(true)
            // Redirect to login after successful registration
            setTimeout(() => {
                navigate('/login')
            }, 2000)
        } catch (err) {
            setError(err.message || 'Failed to register')
        } finally {
            setLoading(false)
        }
    }
    useEffect(() => {
        if (loading) return
        if (isAuthenticated) {
            navigate('/')
        }
        return () => { }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [loading])
    return (
        <div className="flex items-center justify-center flex-1 min-h-full">
            <div className="w-full max-w-md p-8 bg-white rounded-lg shadow-xl bg-opacity-10 backdrop-blur-lg">
                <h1 className="mb-6 text-2xl font-bold text-center text-white">Register</h1>

                {success && (
                    <div className="p-3 mb-4 text-sm text-green-600 rounded-md bg-green-50">
                        Registration successful! Redirecting to login...
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label htmlFor="fullName" className="block mb-1 text-sm font-medium text-white">
                            Full Name (Optional)
                        </label>
                        <input
                            id="fullName"
                            type="text"
                            value={fullName}
                            onChange={(e) => setFullName(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            disabled={loading}
                        />
                    </div>

                    <div>
                        <label htmlFor="email" className="block mb-1 text-sm font-medium text-white">
                            Email
                        </label>
                        <input
                            id="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
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
                            minLength={8}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            disabled={loading}
                        />
                    </div>

                    <div>
                        <label htmlFor="confirmPassword" className="block mb-1 text-sm font-medium text-white">
                            Confirm Password
                        </label>
                        <input
                            id="confirmPassword"
                            type="password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
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
                        {loading ? 'Registering...' : 'Register'}
                    </button>
                </form>

                <div className="mt-6 text-center">
                    <p className="text-sm text-gray-400">
                        Already have an account?{' '}
                        <Link to="/login" className="text-blue-400 hover:text-blue-300">
                            Login here
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    )
}

export default RegisterPage