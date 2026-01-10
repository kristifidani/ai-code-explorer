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
docker compose build frontend
docker compose up -d --wait frontend
```

### NGINX (`nginx.conf`)

The production container serves the built frontend using NGINX, configured in [frontend/nginx.conf](nginx.conf):

- `location /` serves static files and falls back to `index.html` so client-side routes work.
- `location /api/` proxies requests to the backend service URL configured at runtime via `BACKEND_URL`.

This means the browser only talks to a single origin (the frontend origin), and API calls go through `/api/*`.

The frontend uses *two* backend-related variables on purpose:

- `VITE_BACKEND_API_URL` (**build-time, browser-side**) — used by the React app to build `fetch()` URLs.
- Because it is a `VITE_*` variable, it is baked into the JS bundle when you run `npm run build`.
- In the production Docker image we set it to `/api` so the browser calls the same origin (no CORS).

- `BACKEND_URL` (**runtime, container-side**) — used by NGINX to proxy `/api/*` to the real backend.
- This is injected at container runtime (Docker Compose / Railway env vars).
- Example (Docker Compose): `BACKEND_URL=http://backend:8080`
- Example (Railway): `BACKEND_URL=https://<your-backend>.up.railway.app`

Rule of thumb:

- Browser talks to `/api/...` (controlled by `VITE_BACKEND_API_URL=/api`).
- NGINX decides where `/api/...` goes (controlled by `BACKEND_URL=...`).
