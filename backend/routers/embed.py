from fastapi import APIRouter, HTTPException
import os
import chromadb
from chromadb import PersistentClient
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
from backend.routers.chunk import chunk_text

load_dotenv()

router = APIRouter(prefix="/embed", tags=["Embedding"])

EXTRACT_DIR = "extracted_text"
UPLOAD_DIR = "uploaded_pdfs"

# Load API keys
GoogleGenerativeAIEmbeddings.api_key = os.getenv("GOOGLE_API_KEY")

# ---------- NEW Chroma Persistent Client ----------
client = PersistentClient(path="chroma_db")

COLLECTION_NAME = "pdf_collection"


# ---------- Ensure Collection Exists ----------
def get_collection():
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )


# ---------- Embedding Function ----------
def generate_embedding(text: str):
    embedder = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    return embedder.embed_documents([text])[0]


# ---------- API: Embed & Store ----------
@router.post("/{file_id}")
async def embed_and_store(file_id: str):

    text_path = os.path.join(EXTRACT_DIR, f"{file_id}.txt")

    if not os.path.exists(text_path):
        raise HTTPException(status_code=404, detail="Extracted text not found")

    with open(text_path, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text, chunk_size=500, overlap=50)

    collection = get_collection()

    ids = []
    embeddings = []
    metadatas = []
    documents = []

    for i, chunk in enumerate(chunks):
        vector = generate_embedding(chunk)

        ids.append(f"{file_id}_chunk_{i}")
        embeddings.append(vector)
        documents.append(chunk)
        metadatas.append({"file_id": file_id, "chunk_id": i})

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

    return {"message": "Embeddings stored", "file_id": file_id, "total_chunks": len(chunks)}


# ---------- API: Delete File & Embeddings ----------
@router.delete("/{file_id}")
async def delete_file_and_embeddings(file_id: str):

    collection = get_collection()

    # Fetch all vectors for this file
    results = collection.get(where={"file_id": file_id})

    # Delete by IDs
    if results.get("ids"):
        collection.delete(ids=results["ids"])

    # Delete extracted text
    text_file = os.path.join(EXTRACT_DIR, f"{file_id}.txt")
    if os.path.exists(text_file):
        os.remove(text_file)

    # Delete uploaded PDF if needed
    pdf_file = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")
    if os.path.exists(pdf_file):
        os.remove(pdf_file)

    return {"message": "File + embeddings deleted", "file_id": file_id}
