# BlogAgent (The Curator)

Generate technical blog drafts from a single topic using an AI workflow (LangGraph + LangChain).
The web app signs in with Google, then sends a `topic` to the backend to produce a Markdown draft.

## What you get

- An endpoint to generate a full blog outline + sectioned Markdown (`POST /create-blog`)
- Research routing (when the workflow decides web research is needed)
- Frontend preview UI with NextAuth authentication

## Stack

- Frontend: Next.js + NextAuth (Google OAuth)
- Backend: FastAPI + LangGraph/LangChain (Groq + Tavily)
- Database: Postgres (via `DATABASE_URL`)

## Setup

1. Copy the env template:
   - `cp .env.example .env`
2. Fill in the required values in `.env`:
   - `NEXTAUTH_SECRET`
   - `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
   - `DATABASE_URL`
   - `GROQ_API_KEY`
   - `TAVILY_API_KEY`
   - (optional) `NEXT_PUBLIC_API_URL` (defaults to `http://127.0.0.1:4000` in code)

## Run (Docker Compose - recommended)

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:4000

## Run locally (no Docker)

Backend:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn server:app --host 127.0.0.1 --port 4000 --reload
```

Frontend:

```bash
cd ../frontend
npm install
npm run dev
```

## Backend API

`POST /create-blog`

Request body:

```json
{ "topic": "Describe your topic here" }
```

Response:

```json
{ "response": { "...": "draft data" } }
```

## Auth flow (high level)

- User signs in via Google (NextAuth)
- Frontend calls `GET /api/auth/token` to mint a short-lived HS256 JWT using `NEXTAUTH_SECRET`
- Backend validates that JWT with the same `NEXTAUTH_SECRET` and generates the blog draft

## Security note

- `.env` is gitignored, but this repo had real secrets in it previously.
- Those values have been removed/sanitized in this working directory—if you had already shared/committed them elsewhere, you should rotate the impacted keys.

