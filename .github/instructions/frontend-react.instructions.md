---
applyTo: "frontend/**/*.{ts,tsx}"
---

# Frontend React/TypeScript Instructions

## Critical Conventions

**Type Safety:**
- Strict TypeScript, no `any` types
- Backend API types from `types/external.ts`, UI types from `types/internal.ts`

**API Communication:**
- Backend URL from `import.meta.env.VITE_BACKEND_API_URL`
- Responses use `ApiResponse<T>` structure (check `types/external.ts`)

**Security:**
- ALWAYS sanitize with `DOMPurify` before rendering user HTML
- See `ChatBox.tsx` for markdown sanitization pattern

**Component Pattern:**
- Functional components with hooks only

## Key Files

- `App.tsx` — Root component managing application state
- `components/GitHubUpload.tsx` — Upload form with API integration
- `components/ChatBox.tsx` — Chat UI with markdown rendering and sanitization
- `types/external.ts` — Backend API type contracts
- `types/internal.ts` — UI-only types
- `package.json` — Check for scripts and tech stack versions

For more details and complete overview read the `frontend/README.md` and scan the tree structure.
