from milvus_helper.vector_store import get_vector_store
from ingest.ingest import ingest_directory
from dotenv import load_dotenv
from pathlib import Path
import os
from Agents.response_agent import ResponseEngine
from Helpers.file_watcher import start_file_watcher
from Helpers.help_functions import dedupe_ranked_chunks
from threading import Thread

response_engine = ResponseEngine(
    model_name="gpt-4o-mini",
    temperature=0.2,
)

def print_results(results, max_preview_chars=200):
    print("\n--- Ranked Retrieved Chunks (Most Relevant First) ---\n")

    for rank, (doc, score) in enumerate(results, start=1):
        meta = doc.metadata
        content_preview = doc.page_content[:max_preview_chars].replace("\n", " ")

        print(f"[{rank}] score={score:.4f}")
        print(f"  chunk_id      : {meta.get('chunk_id')}")
        print(f"  doc_id        : {meta.get('doc_id')}")
        print(f"  source_type   : {meta.get('source_type')}")
        print(f"  domain        : {meta.get('domain')}")
        print(f"  chunk_index   : {meta.get('chunk_index')}")
        print(f"  prev_chunk_id : {meta.get('prev_chunk_id')}")
        print(f"  next_chunk_id : {meta.get('next_chunk_id')}")
        print(f"  content       : {content_preview}...")
        print("-" * 60)

env_path = Path(".env")
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print("✅ Loaded API key from .env")
else:
    print("⚠️ .env file not found — falling back to system environment or .zprofile")

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("❌ OPENAI_API_KEY not found.")


if __name__ == "__main__":
    vector_store = get_vector_store("knowledge_chunks")

    # Start the file watcher in a separate thread
    def run_file_watcher():
        start_file_watcher(path_to_watch="./data")

    watcher_thread = Thread(target=run_file_watcher, daemon=True)
    watcher_thread.start()

    ingest_directory(
        directory="./data",
        vector_store=vector_store,
        domain="about",  # hardcoded for now
    )

    print("Ingestion complete.")
    print("Type a query to search the knowledge base.")
    print("Type 'exit' to quit.\n")

    # ---- QUERY LOOP ----
    while True:
        query = input("🔎 Query> ").strip()
        if query.lower() in {"exit", "quit"}:
            break

        results = vector_store.similarity_search_with_score(
            query=query,
            k=10,
            # Optional: metadata filtering later
            # filter={"domain": "finance"}
        )
        results = dedupe_ranked_chunks(results)

        if not results:
            print("No results found.\n")
            continue

        print_results(results)

        answer = response_engine.generate_response(
            question=query,
            ranked_chunks=results,
        )

        print("\n🧠 Answer:\n")
        print(answer)
        print("\n" + "=" * 80 + "\n")
