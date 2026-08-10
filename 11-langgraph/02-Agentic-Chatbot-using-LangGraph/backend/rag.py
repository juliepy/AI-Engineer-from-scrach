from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.tools import tool
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.llm import get_embeddings
from backend.logger import get_logger

logger = get_logger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = str(DATA_DIR / "faiss_db")


def ingest_rag_document(file_path: str) -> None:
    logger.info("Ingesting PDF | path=%s", file_path)

    try:
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(docs)
        vector_store = FAISS.from_documents(chunks, get_embeddings())
        vector_store.save_local(DB_PATH)
        logger.info(
            "PDF ingested | docs=%s | chunks=%s | db=%s",
            len(docs),
            len(chunks),
            DB_PATH,
        )
    except Exception:
        logger.exception("PDF ingest failed | path=%s", file_path)
        raise


def get_retriever():
    logger.debug("Loading FAISS retriever | db=%s", DB_PATH)
    vector_store = FAISS.load_local(
        folder_path=DB_PATH,
        embeddings=get_embeddings(),
        allow_dangerous_deserialization=True,
    )

    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4},
    )


@tool
def rag_tool(query: str) -> str:
    """
    Retrieve relevant information from the PDF document.

    Use this tool when the user asks factual or conceptual questions
    that may be answered using the stored PDF documents.

    Args:
        query: The question or search query used to retrieve PDF content.
    """
    logger.info("rag_tool called | query=%s", query[:120])

    try:
        retriever = get_retriever()
        documents = retriever.invoke(query)
    except Exception:
        logger.exception("rag_tool retrieval failed | query=%s", query[:120])
        return "RAG retrieval failed. Please upload a PDF first or try again."

    if not documents:
        logger.warning("rag_tool found no documents | query=%s", query[:120])
        return "No relevant information was found in the PDF."

    logger.info("rag_tool retrieved %s chunks", len(documents))

    formatted_documents = []

    for index, document in enumerate(documents, start=1):
        source = document.metadata.get("source", "Unknown source")
        page = document.metadata.get("page", "Unknown page")

        formatted_documents.append(
            f"Document {index}\n"
            f"Source: {source}\n"
            f"Page: {page}\n"
            f"Content: {document.page_content}"
        )

    return "\n\n".join(formatted_documents)
