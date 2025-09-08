# AI Code Explorer - Frontend

A React frontend for the AI Code Explorer application that allows users to upload GitHub projects and ask questions about the code using AI-powered RAG (Retrieval-Augmented Generation).

## Features

- GitHub project upload via URL
- AI-powered Q&A chat interface about uploaded code
- Clean, minimal UI built with React + Vite

## Tech Stack

- **React 19** - Frontend framework
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool and dev server
- **ESLint** - Code linting

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Type check
npm run tsc

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```text
src/
├── App.tsx          # Main application component
├── App.css          # Application styles
├── index.css        # Global styles
├── main.tsx         # Application entry point
└── assets/          # Static assets
```

## Backend Integration

This frontend connects to:

- **Rust Backend** (port 8080) - Main API server
- **Python AI Service** (port 8000) - AI/RAG processing

Make sure both backend services are running for full functionality.
