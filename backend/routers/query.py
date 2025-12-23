from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import chromadb
import logging
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

router = APIRouter(prefix="/query", tags=["Query"])
logger = logging.getLogger("QueryRouter")

# Persistent client and collection
chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_or_create_collection(name="pdf_collection")

# Embedder
embedder = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

# Request body
class QueryRequest(BaseModel):
    question: str
    file_id: str

@router.post("/")
async def query_pdf(data: QueryRequest):
    logger.info(f"🔎 Query received: file_id={data.file_id}, question={data.question}")
    question = data.question
    file_id = data.file_id

    # 1️⃣ Embed the question
    query_embedding = embedder.embed_query(question)

    # 2️⃣ Run similarity search WITHOUT relying on chunk-specific IDs
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
        where={"file_id": file_id}  # Only main file_id
    )

    documents_list = results.get("documents", [])
    # metadatas_list = results.get("metadatas", [])

    if not documents_list or not documents_list[0]:
        raise HTTPException(404, "No embeddings found for this file.")

    # 3️⃣ Build context from retrieved chunks
    context = "\n\n".join(documents_list[0])

    # 4️⃣ Call LLM with context
    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    prompt = f"""
    You are an expert AI assistant designed to answer user questions strictly using the provided context.

    Follow these rules:
    1. Use ONLY the information present in the context.
    2. Do NOT add assumptions, external knowledge, or invented details.
    3. If the answer is not found in the context, reply with:
    "The information you requested is not available in the document."
    4. Keep the answer concise (4–5 lines), clear, and user-friendly.
    5. Maintain accuracy and avoid repetition.

    -----------------------------
    CONTEXT:
    {context}
    -----------------------------

    USER QUESTION:
    {question}

    Now provide the best possible answer based only on the context.
    """
    
    llm_response = model.invoke(prompt)
    answer = llm_response.content

    # 5️⃣ Return answer
    
    return {
        "answer": answer
    }
    
