import root_env  # noqa: F401 — repo-root `.env` before workflow / jwt

from datetime import datetime

import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend import workflow
from jwt_auth import require_nextauth_user

import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Fetch variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Connect to the database
connection = psycopg2.connect(DATABASE_URL)

print(connection)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; can be tightened later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Blog_Requirements(BaseModel):
    topic: str


@app.post("/create-blog")
def create_blog(
    body: Blog_Requirements,
    _claims: dict = Depends(require_nextauth_user),
):

#https://cmwllmzauncixcfjlcyq.supabase.co/Blog_Info , db API



    print(_claims.sub)

    


    response = workflow.invoke(
        {
            "topic": body.topic,
            "as_of": datetime.now().strftime("%m/%d/%Y"),
        }
    )

    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=4000)