# TOP Movie Recommender - Frontend

React + Vite + Tailwind CSS frontend application for the TOP Movie Recommender system.

## Tech Stack

- **React 18**: Modern React with hooks
- **Vite**: Next-generation frontend tooling
- **Tailwind CSS**: Utility-first CSS framework
- **React Router DOM**: Client-side routing
- **Axios**: Promise-based HTTP client
- **Docker**: Containerization with Nginx

## Project Structure

```
front-end/
├── src/
│   ├── components/         # Reusable React components
│   │   ├── Layout.jsx     # Main layout wrapper
│   │   ├── SearchInput.jsx # Search input with debounce
│   │   ├── MovieCard.jsx  # Individual movie card
│   │   └── MovieList.jsx  # Grid of movie cards
│   ├── pages/             # Page components
│   │   ├── SearchPage.jsx # Main search page
│   │   ├── MovieDetailsPage.jsx # Movie details view
│   │   └── NotFound.jsx   # 404 page
│   ├── services/          # API services
│   │   └── movieService.js # Movie API calls
│   ├── App.jsx            # Main app component
│   ├── main.jsx           # Entry point
│   └── index.css          # Global styles
├── public/                # Static assets
├── Dockerfile             # Multi-stage Docker build
├── docker-compose.yml     # Docker Compose configuration
├── nginx.conf             # Nginx configuration
├── vite.config.js         # Vite configuration
├── tailwind.config.js     # Tailwind configuration
└── package.json           # Dependencies and scripts
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
  or
- Docker

### Installation

1. **Install dependencies:**

   ```bash
   npm install
   ```

2. **Configure environment variables:**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set your API base URL:

   ```
   VITE_API_BASE_URL=http://localhost:8000/api
   ```

3. **Start development server:**

   ```bash
   npm run dev
   ```

   The application will be available at `http://localhost:3000`

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint

## Docker Deployment

### Build and run with Docker:

```bash
# Build the image
docker build -t top-recommender-frontend .

# Run the container
docker run -p 3000:80 top-recommender-frontend
```

### Using Docker Compose:

```bash
docker-compose up -d
```

The application will be available at `http://localhost:3000`
