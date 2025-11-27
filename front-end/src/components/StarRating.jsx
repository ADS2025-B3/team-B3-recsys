import { useState } from 'react'

/**
 * StarRating Component
 * Interactive star rating component that allows users to select a rating from 1 to 5
 * @param {number} value - Current rating value (1-5)
 * @param {function} onChange - Callback function when rating changes
 * @param {boolean} disabled - Whether the rating is disabled
 * @param {boolean} readOnly - Whether the rating is read-only (shows value but no interaction)
 */
function StarRating({ value = 0, onChange, disabled = false, readOnly = false }) {
    const [hoverValue, setHoverValue] = useState(0)

    const handleClick = (rating) => {
        if (!disabled && !readOnly && onChange) {
            onChange(rating)
        }
    }

    const handleMouseEnter = (rating) => {
        if (!disabled && !readOnly) {
            setHoverValue(rating)
        }
    }

    const handleMouseLeave = () => {
        setHoverValue(0)
    }

    const getStarClass = (index) => {
        const rating = hoverValue || value
        const baseClass = "w-8 h-8 transition-all duration-150"
        const interactiveClass = !disabled && !readOnly ? "cursor-pointer hover:scale-110" : ""
        const colorClass = index <= rating
            ? "text-yellow-400"
            : "text-gray-300 dark:text-gray-600"
        const disabledClass = disabled ? "opacity-50 cursor-not-allowed" : ""

        return `${baseClass} ${interactiveClass} ${colorClass} ${disabledClass}`.trim()
    }

    return (
        <div className="flex items-center space-x-1">
            {[1, 2, 3, 4, 5].map((star) => (
                <button
                    key={star}
                    type="button"
                    onClick={() => handleClick(star)}
                    onMouseEnter={() => handleMouseEnter(star)}
                    onMouseLeave={handleMouseLeave}
                    disabled={disabled || readOnly}
                    className={getStarClass(star)}
                    aria-label={`Rate ${star} out of 5 stars`}
                >
                    <svg
                        fill="currentColor"
                        viewBox="0 0 20 20"
                        xmlns="http://www.w3.org/2000/svg"
                    >
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                </button>
            ))}
            {!readOnly && (
                <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">
                    {value > 0 ? `${value}/5` : 'Select rating'}
                </span>
            )}
        </div>
    )
}

export default StarRating
