import { useState, useEffect } from 'react'
import { getAvailableGenres, saveUserPreferences, updateUserPreferences } from '../services/preferencesService'
import { useSession } from '../context/SessionContext'

function PreferencesModal({ isOpen, onClose, open, existingPreferences = null, isRequired = false }) {
    const [genres, setGenres] = useState([])
    const [selectedGenres, setSelectedGenres] = useState([])
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)
    const [error, setError] = useState('')
    const [success, setSuccess] = useState('')
    const { token } = useSession()

    useEffect(() => {
        if (genres.length === 0) loadGenres()
        if (isOpen && existingPreferences?.preferred_genres.length > 0) {
            setSelectedGenres(existingPreferences.preferred_genres)
            return
        }
        if (existingPreferences?.preferred_genres.length === 0) {
            open()
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [isOpen, existingPreferences])

    const loadGenres = async () => {
        try {
            setLoading(true)
            setError('')
            const genreList = await getAvailableGenres()

            // Parse genres from the format "Adventure|Children|Fantasy"
            const uniqueGenres = new Set()
            genreList.forEach(genreString => {
                if (genreString) {
                    const genreArray = genreString.split('|')
                    genreArray.forEach(genre => {
                        if (genre.trim()) {
                            uniqueGenres.add(genre.trim())
                        }
                    })
                }
            })

            setGenres(Array.from(uniqueGenres).sort())
        } catch (err) {
            setError(err.message || 'Failed to load genres')
        } finally {
            setLoading(false)
        }
    }

    const toggleGenre = (genre) => {
        setSelectedGenres(prev => {
            if (prev.includes(genre)) {
                return prev.filter(g => g !== genre)
            } else {
                return [...prev, genre]
            }
        })
        setError('')
        setSuccess('')
    }

    const handleSave = async () => {
        if (selectedGenres.length === 0) {
            setError('Please select at least one genre')
            return
        }

        try {
            setSaving(true)
            setError('')
            setSuccess('')

            // If preferences exist, update them; otherwise create new
            if (existingPreferences.preferred_genres.length > 0) {
                await updateUserPreferences(token, selectedGenres)
                setSuccess('Preferences updated successfully!')
            } else {
                await saveUserPreferences(token, selectedGenres)
                setSuccess('Preferences saved successfully!')
            }

            // Close modal after a brief delay to show success message
            setTimeout(() => {
                onClose(true) // Pass true to indicate preferences were saved
            }, 500)
        } catch (err) {
            setError(err.message || 'Failed to save preferences')
        } finally {
            setSaving(false)
        }
    }

    const handleClose = () => {
        if (!isRequired) {
            onClose(false)
        }
    }

    if (!isOpen) return null

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
            <div className="w-full max-w-2xl p-6 bg-gray-800 rounded-lg shadow-xl max-h-[90vh] overflow-y-auto">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-2xl font-bold text-white">
                        {existingPreferences.preferred_genres.length > 0 ? 'Edit Your Preferences' : 'Select Your Preferences'}
                    </h2>
                    {!isRequired && (
                        <button
                            onClick={handleClose}
                            className="text-gray-400 hover:text-gray-200"
                            disabled={saving}
                        >
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    )}
                </div>

                {isRequired && (
                    <div className="p-3 mb-4 text-sm text-blue-200 bg-blue-900 rounded-md">
                        Please select your preferred genres to get personalized movie recommendations!
                    </div>
                )}

                {loading ? (
                    <div className="py-8 text-center text-gray-400">
                        Loading genres...
                    </div>
                ) : (
                    <>
                        <div className="mb-4">
                            <p className="text-sm text-gray-400">
                                Select one or more genres you enjoy:
                            </p>
                        </div>

                        <div className="grid grid-cols-2 gap-3 mb-6 sm:grid-cols-3">
                            {genres.map((genre) => (
                                <button
                                    key={genre}
                                    onClick={() => toggleGenre(genre)}
                                    className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${selectedGenres.includes(genre)
                                        ? 'bg-blue-600 text-white hover:bg-blue-700'
                                        : 'bg-gray-700 text-gray-200 hover:bg-gray-600'
                                        }`}
                                    disabled={saving}
                                >
                                    {genre}
                                </button>
                            ))}
                        </div>

                        {selectedGenres.length > 0 && (
                            <div className="p-3 mb-4 rounded-md bg-gray-700">
                                <p className="text-sm font-medium text-gray-300">
                                    Selected: {selectedGenres.join(', ')}
                                </p>
                            </div>
                        )}

                        {error && (
                            <div className="p-3 mb-4 text-sm text-red-200 bg-red-900 rounded-md">
                                {error}
                            </div>
                        )}

                        {success && (
                            <div className="p-3 mb-4 text-sm text-green-200 bg-green-900 rounded-md">
                                {success}
                            </div>
                        )}

                        <div className="flex justify-end space-x-3">
                            {!isRequired && (
                                <button
                                    onClick={handleClose}
                                    className="px-4 py-2 text-gray-300 transition-colors bg-gray-700 rounded-md hover:bg-gray-600"
                                    disabled={saving}
                                >
                                    Cancel
                                </button>
                            )}
                            <button
                                onClick={handleSave}
                                className="px-4 py-2 text-white transition-colors bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                                disabled={saving || selectedGenres.length === 0}
                            >
                                {saving ? 'Saving...' : 'Save Preferences'}
                            </button>
                        </div>
                    </>
                )}
            </div>
        </div>
    )
}

export default PreferencesModal
