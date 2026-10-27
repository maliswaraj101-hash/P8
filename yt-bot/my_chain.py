from langchain_huggingface import ChatHuggingFace , HuggingFaceEndpoint
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable import RunnableSequence , RunnableLambda , RunnableParallel , RunnablePassthrough
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from youtube_transcript_api import YouTubeTranscriptApi
import os


load_dotenv()

def get_model():
    llm = HuggingFaceEndpoint(


    repo_id = "google/gemma-2-2b-it",
    huggingfacehub_api_token = os.getenv("HUGGINGFACEHUB_API_KEY"),
    task = "text-generation"
    )
    model = ChatHuggingFace(llm = llm)
    return model


def get_transcript_chunks(video_id: str):
    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch(video_id)
    # https://www.youtube.com/watch?v=qjPH9njnaVU
    transcript_text = ""
    transcript_text = "".join(snippet.text for snippet in transcript)
    splitter = RecursiveCharacterTextSplitter(chunk_size = 1000 , chunk_overlap = 200)
    chunks = splitter.create_documents([transcript_text])
    return chunks



def get_vector_store(chunks):
    embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
    hf = HuggingFaceEndpointEmbeddings(
    model=embedding_model,
    task="feature-extraction",
    huggingfacehub_api_token= os.getenv("HUGGINGFACEHUB_API_KEY"),
    )
    vector_store = FAISS.from_documents(chunks, hf) 
    return vector_store
# chunks are converted to embeddings and stored in vector store


def get_prompt():
    prompt = PromptTemplate(
        template="""
        You are a helpful assistant.
        Answer only from the provided transcript context.
        If the context is insufficient , just say you don't know.
        {context}
        Question : {question} \n
        Conversation so far : {history}
        """,
        input_variables=['context', 'question' , 'history']
    )

    return prompt



def format_docs(context):
    context_text = "\n\n".join(doc.page_content for doc in context)
    return context_text

store = {}

def get_session_history(session_id : str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id] 


def get_final_chain(video_id : str):
    model = get_model()
    chunks = get_transcript_chunks(video_id)
    vector_store = get_vector_store(chunks)
    retriever = vector_store.as_retriever(search_type = 'similarity' , search_kwargs = {"k" : 5})
    prompt = get_prompt()
    parser = StrOutputParser()

    chain = prompt | model | parser
    parallel_chain = RunnableParallel({
        "context" : retriever | RunnableLambda(format_docs),
        "question" : RunnablePassthrough(),
    })
    
    chain_with_memory =  RunnableWithMessageHistory(
    runnable = chain,
    get_session_history=get_session_history,
    input_messages_key="question",
    history_messages_key="history"
    )
    
    final_chain = parallel_chain | chain_with_memory
    return final_chain




if __name__ == "__main__":

    final_chain = get_final_chain("qjPH9njnaVU")
    result = final_chain.invoke(
    "Tell me about Romanian elections",
    config={'configurable': {"session_id": "user1"}}
    )
    
    print(result)


