from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def chunk_documents(
    docs: list[Document],
    doc_id: str,
    domain: str,
    source_type: str,
):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=300,
        separators=["\n\n", "\n", ".", " ", ""],
    )

    chunks = splitter.split_documents(docs)
    total_chunks = len(chunks)
    enriched_chunks = []

    for idx, chunk in enumerate(chunks):
        metadata = {
            "chunk_id": f"{doc_id}_chunk_{idx}",
            "doc_id": doc_id,
            "chunk_index": idx,
            "domain": domain,
            "source_type": source_type,
            "status": "active",
            "prev_chunk_id": f"{doc_id}_chunk_{idx-1}" if idx > 0 else "",
            "next_chunk_id": f"{doc_id}_chunk_{idx+1}" if idx < total_chunks - 1 else "",
        }

        enriched_chunks.append(
            Document(
                page_content=chunk.page_content,
                metadata=metadata,
            )
        )

    return enriched_chunks
