import { useState, useEffect } from 'react'

function SearchInput({ onSearch, placeholder = "Search for movies..." }) {
    const [searchTerm, setSearchTerm] = useState('')

    // Debounce effect - delays API call until user stops typing
    useEffect(() => {
        const debounceTimer = setTimeout(() => {
            if (searchTerm.trim()) {
                onSearch(searchTerm)
            }
        }, 500) // 500ms delay

        return () => clearTimeout(debounceTimer)
    }, [searchTerm, onSearch])

    const handleChange = (e) => {
        setSearchTerm(e.target.value)
    }

    const handleSubmit = (e) => {
        e.preventDefault()
        if (searchTerm.trim()) {
            onSearch(searchTerm)
        }
    }

    const handleClear = () => {
        setSearchTerm('')
    }

    return (
        <form onSubmit={handleSubmit} className="w-full max-w-3xl mx-auto">
            <div className="relative">
                <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                    <svg
                        className="w-5 h-5 text-gray-400"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                        />
                    </svg>
                </div>
                <input
                    type="text"
                    value={searchTerm}
                    onChange={handleChange}
                    placeholder={placeholder}
                    className="input-field pl-10 pr-20"
                />
                {searchTerm && (
                    <button
                        type="button"
                        onClick={handleClear}
                        className="absolute inset-y-0 right-12 flex items-center pr-3 text-gray-400 hover:text-gray-300"
                    >
                        <svg
                            className="w-5 h-5"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M6 18L18 6M6 6l12 12"
                            />
                        </svg>
                    </button>
                )}
                <button
                    type="submit"
                    className="absolute inset-y-0 right-0 flex items-center px-4 text-white bg-primary-600 rounded-r-lg hover:bg-primary-700 focus:ring-4 focus:outline-none focus:ring-primary-300"
                >
                    Search
                </button>
            </div>
        </form>
    )
}

export default SearchInput
