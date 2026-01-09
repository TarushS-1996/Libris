import sys
from pathlib import Path

# Add the project directory to sys.path
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from milvus_helper.vector_store import get_vector_store
from ingest.ingest import ingest_directory
from dotenv import load_dotenv
from pathlib import Path
import os
from Agents.response_agent import ResponseEngine
from Helpers.file_watcher import start_file_watcher
from Helpers.help_functions import dedupe_ranked_chunks
from threading import Thread
from pydantic import BaseModel
from threading import Thread


env_path = Path(".env")
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print("✅ Loaded API key from .env")
else:
    print("⚠️ .env file not found — falling back to system environment or .zprofile")

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("❌ OPENAI_API_KEY not found.")


app = FastAPI()
response_engine = ResponseEngine(
    model_name="gpt-4o-mini",
    temperature=0.2,
)






env_path = Path(".env")
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print("✅ Loaded API key from .env")
else:
    print("⚠️ .env file not found — falling back to system environment or .zprofile")

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("❌ OPENAI_API_KEY not found.")


app = FastAPI()
response_engine = ResponseEngine(
    model_name="gpt-4o-mini",
    temperature=0.2,
)


@app.on_event("startup")
async def startup_event():
    app.state.vector_store = get_vector_store("knowledge_chunks")

    ingest_directory(
        directory="./data",
        vector_store=app.state.vector_store,
        domain="about",
    )

    Thread(
        target=start_file_watcher,
        kwargs={"path_to_watch": "./data"},
        daemon=True,
    ).start()

class QueryRequest(BaseModel):
    query: str

@app.post("/get-response")
async def get_response(request: QueryRequest):
    vector_store = app.state.vector_store
    query = request.query

    results = vector_store.similarity_search_with_score(
        query=query,
        k=10,
    )

    deduped_results = dedupe_ranked_chunks(results)

    answer = response_engine.generate_response(
        question=query,
        ranked_chunks=deduped_results,
    )

    return {"answer": answer}

