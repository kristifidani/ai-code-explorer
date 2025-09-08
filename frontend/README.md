# AI Code Explorer - Frontend

A React frontend for the AI Code Explorer application that allows users to upload GitHub projects and ask questions about the code using AI-powered RAG (Retrieval-Augmented Generation).

## Features

- GitHub project upload via URL
- AI-powered Q&A chat interface about uploaded code
- Clean, minimal UI built with React + TypeScript + Vite

## Tech Stack

Our frontend uses a modern, lightweight stack optimized for rapid development and type safety:

- **React 19** - Component-based UI framework for building interactive interfaces
- **TypeScript** - Adds static typing to catch errors early and improve code reliability
- **Vite** - Lightning-fast build tool with instant hot module replacement
- **ESLint** - Code linting with type-aware rules for TypeScript

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
