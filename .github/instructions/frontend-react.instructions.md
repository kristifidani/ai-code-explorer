---
applyTo: "frontend/**/*.{ts,tsx}"
---

# Frontend React/TypeScript Instructions

## Critical Conventions

**Type Safety:**
- Strict TypeScript — no `any` types
- Properly type all component props, state, and event handlers
- Import backend API types from `src/types/external.ts`

**Security:**
- Always use `DOMPurify.sanitize()` before rendering user-generated HTML content
- See `ChatBox.tsx` for example of sanitizing markdown before rendering

**Tech Stack:**
- React 19 with functional components and hooks
- Tailwind CSS 4 for styling
- Vite 7 for build tooling
- markdown-it for markdown parsing + DOMPurify for sanitization

## Key Files

- `src/App.tsx` — Main component orchestrating UI
- `src/components/GitHubUpload.tsx` — Upload interface
- `src/components/ChatBox.tsx` — Q&A interface with markdown rendering
- `src/types/external.ts` — Backend API type definitions
- `src/types/internal.ts` — Frontend-only types
- `package.json` — Scripts and dependencies

**For implementation details:** Read existing code to understand file relationships and development patterns. Keep it consistent.
