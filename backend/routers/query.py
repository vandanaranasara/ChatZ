from fastapi import APIRouter, HTTPException
import chromadb
from chromadb.config import Settings
from langchain_google_genai import GoogleGenerativeAIEmbeddings,ChatGoogleGenerativeAI
from typing import List

router = APIRouter(prefix="/query", tags=["Query"])

chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_or_create_collection(
    name="pdf_embeddings",
    metadata={"hnsw:space": "cosine"}
)

embedder = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

@router.post("/")
async def query_pdf(question: str, file_id: str):
    query_embedding = embedder.embed_query(question)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
        where={"file_id": file_id}
    )

    chunks = results["documents"][0]
    metadatas = results["metadatas"][0]

    # Create answer context
    context = "\n\n".join(chunks)

    # Call Gemini to generate answer using retrieved context

    model = ChatGoogleGenerativeAI(model="gemini-2.5-pro")

    prompt = f"""
    You are a PDF question-answering AI. 
    Use ONLY the context given below to answer.

    CONTEXT:
    {context}

    QUESTION:
    {question}

    Return answer in 4-5 lines.
    """

    llm_response = model.invoke(prompt)

    answer = llm_response.text

    return {
        "answer": answer,
        "sources": [
            {
                "text": m["text"],
                "page": m.get("page", "Unknown")
            }
            for m in metadatas
        ]
    }
