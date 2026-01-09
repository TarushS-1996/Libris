import os
from ingest.loaders import load_file
from ingest.chunker import chunk_documents
from milvus_helper.vector_store import get_vector_store


def ingest_directory(
    directory: str,
    vector_store,
    domain: str,
):
    for root, _, files in os.walk(directory):
        for file in files:
            if not file.endswith((".pdf", ".docx", ".txt")):
                continue

            path = os.path.join(root, file)
            path = os.path.abspath(path)
            print(f"Ingesting: {path}")

            doc_id = f"file:{path}"
            source_type = file.split(".")[-1]

            docs = load_file(path)
            for i, doc in enumerate(docs):
                print(f"\n--- RAW PAGE {i} ---\n")
                print(doc.page_content[:1500])

            chunks = chunk_documents(
                docs=docs,
                doc_id=doc_id,
                domain=domain,
                source_type=source_type,
            )

            vector_store.add_documents(chunks)
            print(f"Added {len(chunks)} chunks from {path} to vector store.")

def ingest_file(
    file_path: str,
    vector_store,
    domain: str,
):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    print(f"Ingesting file: {file_path}")
    doc_id_path = os.path.abspath(file_path)
    doc_id = f"file:{doc_id_path}"

    source_type = file_path.split(".")[-1]

    docs = load_file(file_path)

    chunks = chunk_documents(
        docs=docs,
        doc_id=doc_id,
        domain=domain,
        source_type=source_type,
    )

    vector_store.add_documents(chunks)
    print(f"Added {len(chunks)} chunks from {file_path} to vector store.")

def delete_file_from_vector_store(file_path: str, vector_store):
    import os

    path = os.path.abspath(file_path)
    doc_id = f"file:{path}"

    print(f"Deleting doc_id: {doc_id}")

    try:
        vector_store.delete(
            expr=f'doc_id == "{doc_id}"'
        )
        print(f"✅ Deleted chunks for {doc_id}")

    except Exception as e:
        print(f"❌ Failed to delete {doc_id}: {e}")