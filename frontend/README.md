# Frontend

A React frontend application that allows users to upload GitHub projects and offers a Q&A chat interface.

## Tech Stack

Our frontend uses a modern, lightweight stack optimized for rapid development and type safety:

- **React 19** - Component-based UI framework for building interactive interfaces.
- **TypeScript** - Adds static typing to catch errors early and improve code reliability.
- **Vite** - Lightning-fast build tool with instant hot module replacement.
- **ESLint** - Code linting with type-aware rules for TypeScript.

This combination provides excellent developer experience with fast builds, strong typing for our API integrations, and a minimal setup that scales well. Perfect for building forms, chat interfaces, and handling API responses from our multi-service backend.

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Lint code
npm run lint

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```text
src/
├── App.tsx          # Main application component
├── index.css        # Global styles
├── main.tsx         # Application entry point
├── types/           # Internal and external types.
└── components/      # UI components.
```

## Running the Frontend

- Using npm (local development):

```bash
npm run dev
```

- Using Docker Compose:

```bash
docker compose --profile local build frontend
docker compose --profile local up -d --wait frontend
```

### NGINX (`nginx.conf`)

The production container serves the built frontend using NGINX, configured in [frontend/nginx.conf](nginx.conf):

- `location /` serves static files and falls back to `index.html` so client-side routes work.
- `location /api/` proxies requests to the backend container (`http://backend:8080/`).

This means the browser only talks to a single origin (the frontend origin), and API calls go through `/api/*`.  
For local development (running `npm run dev` outside Docker), set `VITE_BACKEND_API_URL` in your local `.env` (for example `http://localhost:8080`)

### Backend Integration

This frontend connects to:

- **Rust Backend** (port 8080) - Main API server.

Make sure both backend services are running for full functionality.
