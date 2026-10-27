# YouTube RAG Bot

Chat with any YouTube video using Retrieval-Augmented Generation (RAG). The app fetches the video transcript, embeds it into a FAISS vector store, and answers questions only from that context — with optional conversation memory.

## Features

- Fetch transcripts via `youtube-transcript-api`
- Chunk + embed with Hugging Face (`sentence-transformers/all-MiniLM-L6-v2`)
- Similarity retrieval (top-k) into a grounded prompt
- FastAPI endpoint for per-video Q&A with session history
- Exploration notebooks using Hugging Face and Groq models

## Project structure

| File | Role |
|------|------|
| `main.py` | FastAPI app — `POST /predict/` |
| `my_chain.py` | RAG pipeline (transcript → FAISS → LLM + memory) |
| `main.ipynb` / `final.ipynb` | Notebook prototypes |
| `.env.example` | Required env var names (copy to `.env`) |

## Prerequisites

- Python 3.10+
- A [Hugging Face](https://huggingface.co/settings/tokens) API token
- (Optional, for notebooks) a [Groq](https://console.groq.com/keys) API key

## Setup

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Copy the example env file and add your keys:

```bash
cp .env.example .env
```

Edit `.env`:

```
GROQ_API_KEY=your_groq_api_key_here
HUGGINGFACEHUB_API_KEY=your_huggingface_api_key_here
```

Never commit `.env`. It is listed in `.gitignore`.

## Run the API

```bash
uvicorn main:app --reload
```

### `POST /predict/`

```json
{
  "UserMessage": "What is the main topic of this video?",
  "session_id": "user1",
  "video_id": "qjPH9njnaVU"
}
```

`video_id` is the YouTube ID from `https://www.youtube.com/watch?v=<video_id>`.

Example response:

```json
{
  "response": "..."
}
```

## How it works

1. Load the transcript for `video_id`
2. Split into overlapping chunks
3. Embed chunks and store in FAISS
4. Retrieve relevant chunks for the user question
5. Prompt the LLM with context + chat history; answer only from the transcript

## Security

- API keys live only in `.env` (local, gitignored)
- Use `.env.example` as a template — no real secrets in the repo
- If a key was ever committed or shared, rotate it on Hugging Face / Groq

## License

MIT
