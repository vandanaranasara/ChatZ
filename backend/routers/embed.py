from fastapi import APIRouter, HTTPException
import os
import logging
from chromadb import PersistentClient
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
from backend.database import SessionLocal
from backend.models import FileInfo
from backend.routers.chunk import chunk_text

load_dotenv()

router = APIRouter(prefix="/embed", tags=["Embedding"])
logger = logging.getLogger("EmbedRouter")

EXTRACT_DIR = "extracted_text"
UPLOAD_DIR = "uploaded_pdfs"

client = PersistentClient(path="chroma_db")


def get_collection():
    return client.get_or_create_collection(
        name="pdf_collection",
        metadata={"hnsw:space": "cosine"}
    )


def generate_embedding(text: str):
    embedder = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    return embedder.embed_documents([text])[0]


@router.post("/{file_id}")
async def embed_and_store(file_id: str):
    logger.info(f"Embedding request: {file_id}")
    text_path = os.path.join(EXTRACT_DIR, f"{file_id}.txt")

    if not os.path.exists(text_path):
        raise HTTPException(status_code=404, detail="Extracted text not found")

    # Read extracted text
    with open(text_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Chunk text
    chunks = chunk_text(text, chunk_size=700, overlap=100)

    collection = get_collection()

    ids, embeddings, documents, metadatas = [], [], [], []

    for i, chunk in enumerate(chunks):
        vector = generate_embedding(chunk)
        ids.append(f"{file_id}_chunk_{i}")
        embeddings.append(vector)
        documents.append(chunk)
        metadatas.append({
            "file_id": file_id,
            "chunk_id": i
        })

    # Store in Chroma
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

    # ---------------- UPDATE DB embedding_status = True -----------------
    db = SessionLocal()
    record = db.query(FileInfo).filter(FileInfo.file_id == file_id).first()

    if record:
        record.embedding_status = True
        db.commit()

    # ---------------- DELETE extracted text file silently ---------------
    try:
        if os.path.exists(text_path):
            os.remove(text_path)        # 🔥 Silent deletion
    except Exception as e:
        # Log the error but DO NOT send to API response
        logger.error(f"Failed to delete extracted file: {e}")

    return {
        "message": "Embedding completed",
        "file_id": file_id,
        "total_chunks": len(chunks)
    }

# from fastapi import APIRouter, HTTPException
# import os
# import logging
# from chromadb import PersistentClient
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from dotenv import load_dotenv
# from backend.database import SessionLocal
# from backend.models import FileInfo
# from backend.routers.chunk import chunk_text

# load_dotenv()

# router = APIRouter(prefix="/embed", tags=["Embedding"])
# logger = logging.getLogger("EmbedRouter")

# EXTRACT_DIR = "extracted_text"
# UPLOAD_DIR = "uploaded_pdfs"

# client = PersistentClient(path="chroma_db")


# def get_collection():
#     return client.get_or_create_collection(
#         name="pdf_collection",
#         metadata={"hnsw:space": "cosine"}
#     )


# def generate_embedding(text: str):
#     embedder = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
#     return embedder.embed_documents([text])[0]


# @router.post("/{file_id}")
# async def embed_and_store(file_id: str):
#     logger.info(f"Embedding request: {file_id}")
#     text_path = os.path.join(EXTRACT_DIR, f"{file_id}.txt")

#     if not os.path.exists(text_path):
#         raise HTTPException(status_code=404, detail="Extracted text not found")

#     with open(text_path, "r", encoding="utf-8") as f:
#         text = f.read()

#     chunks = chunk_text(text, chunk_size=700, overlap=100)

#     collection = get_collection()

#     ids, embeddings, documents, metadatas = [], [], [], []

#     for i, chunk in enumerate(chunks):
#         vector = generate_embedding(chunk)
#         ids.append(f"{file_id}_chunk_{i}")
#         embeddings.append(vector)
#         documents.append(chunk)
#         metadatas.append({"file_id": file_id, "chunk_id": i})

#     collection.add(
#         ids=ids,
#         embeddings=embeddings,
#         documents=documents,
#         metadatas=metadatas
#     )

#     # -------------- UPDATE DB embedding_status = True --------------------
#     db = SessionLocal()
#     record = db.query(FileInfo).filter(FileInfo.file_id == file_id).first()

#     if record:
#         record.embedding_status = True
#         db.commit()

#     return {
#         "message": "Embedding completed",
#         "file_id": file_id,
#         "total_chunks": len(chunks)
#     }


