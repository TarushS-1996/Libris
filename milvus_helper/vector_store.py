from langchain_milvus import Milvus
from langchain_openai import OpenAIEmbeddings
import os

def get_vector_store(collection_name: str):
    embeddings = OpenAIEmbeddings()

    # Milvus Lite (embedded, file-based)
    db_path = os.path.abspath("knowledgeBase/milvus.db")

    vector_store = Milvus(
        embedding_function=embeddings,
        collection_name=collection_name,
        connection_args={
            "uri": db_path
        },
    )

    return vector_store
