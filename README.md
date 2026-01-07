# AI Code Explorer

> Transform how you interact with your codebase using AI-powered semantic search and natural language understanding.

## Overview

AI Code Explorer is an intelligent developer assistant that enables advanced semantic search and natural language Q&A directly over your source code. By combining code embeddings, vector databases, and large language models, it helps you quickly understand, navigate, and reason about complex projects—making your development workflow faster and more intuitive.

## Architecture

The system consists of three main services working together:

### [AI Service](ai-service/README.md)

Core RAG engine providing semantic codebase search and intelligent Q&A capabilities. Handles code embeddings, vector storage, and LLM integration.

### [Backend](backend/README.md)

High-performance API gateway managing request routing, validation, and coordination between frontend and AI service.

### [Frontend](frontend/README.md)

Modern web interface for uploading GitHub repositories and interactive code exploration with real-time Q&A.
