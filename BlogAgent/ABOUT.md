# About

“The Curator” is an AI-assisted technical writing workflow that turns a topic into a structured, publish-ready Markdown draft.

At a high level, the pipeline works like this:

1. **Routing**: The workflow decides whether the blog can be written from evergreen knowledge or whether it needs web research.
2. **Research (optional)**: When research is needed, it uses **Tavily** to gather evidence, then converts results into structured “evidence” items.
3. **Planning**: Using the evidence (or “closed book” assumptions), it generates a plan: blog title, audience, tone, and a set of tasks/sections.
4. **Section writing (worker)**: Each section is written in Markdown by the model, following the plan’s constraints.

## Modes

- `closed_book`: no web research; evergreen concepts
- `hybrid`: mix of evergreen + evidence-backed examples
- `open_book`: news/rapidly changing topics; uses recent evidence where available

## Project components

- **Frontend (Next.js)**: Google sign-in with NextAuth + a simple UI that calls the backend to generate drafts.
- **Backend (FastAPI)**: Auth validation + orchestration endpoint (`POST /create-blog`).
- **Workflow (LangGraph/LangChain)**: routing → (optional) research → planning → worker section generation.

## Notes on secrets

This repo is set up to read all credentials from the repo-root `.env` file (loaded by the backend and Next.js at runtime). Real keys should never be stored directly in source code or committed to the repo.

