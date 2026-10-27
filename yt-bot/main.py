from fastapi import FastAPI
from pydantic import BaseModel
from my_chain import get_final_chain
from fastapi.middleware.cors import CORSMiddleware




app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Query(BaseModel) :
    UserMessage : str
    session_id : str    
    video_id : str

chains = {}

def get_chain_for_video(video_id : str):
    if video_id not in chains:
        chains[video_id] = get_final_chain(video_id)
    return chains[video_id]

@app.post("/predict/")
async def LLMQuery(query :  Query):

    chain = get_chain_for_video(query.video_id)

    response = chain.invoke(
        f"{query.UserMessage}",
        config = {'configurable' : {"session_id" : f"{query.session_id}"}}
    )

    return {"response" : response}