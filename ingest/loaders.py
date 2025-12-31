from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader,
)

from langchain_community.document_loaders import UnstructuredPDFLoader

def load_file(path: str):
    if path.endswith(".pdf"):
        return UnstructuredPDFLoader(path, mode="single").load()
    elif path.endswith(".docx"):
        return UnstructuredWordDocumentLoader(path).load()
    elif path.endswith(".txt"):
        return TextLoader(path).load()
    else:
        raise ValueError(f"Unsupported file type: {path}")