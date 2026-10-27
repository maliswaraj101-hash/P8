from fastapi import FastAPI, File, UploadFile, Body
import uvicorn
import logging
from pydantic import BaseModel
from langgraph.types import Command

# Configure logging to show INFO messages
logging.basicConfig(level=logging.INFO)
from fastapi.middleware.cors import CORSMiddleware
from server import workflow

app = FastAPI()

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ocr")
async def get_docs_for_ocr(file: UploadFile = File(...)):
    logging.info(f"this is the file {file}")
    content = await file.read()

    config = {
        "configurable": {
            "thread_id": "1"
        }
    }
    result = await workflow.ainvoke({
        "standard":"Schedule 3",
        "document" : content
    } , config )

    # Remove binary document from result to avoid FastAPI serialization errors
    if "document" in result:
        del result["document"]
    
    logging.info(f"this is the result {result}")

    return result

class ResumeRequest(BaseModel):
    thread_id: str
    approval: str

@app.post("/resume")
async def resume_workflow(request: ResumeRequest):
    logging.info(f"Resuming workflow for thread {request.thread_id} with approval: {request.approval}")
    
    config = {
        "configurable": {
            "thread_id": request.thread_id
        }
    }
    
    # Use Command to resume the workflow from the interrupt point
    result = await workflow.ainvoke(Command(resume=request.approval), config=config)
    # request.approval is the value which is yes or no and is returned to interrupt

    # Cleanup result for response
    if "document" in result:
        del result["document"]
        
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=4000)