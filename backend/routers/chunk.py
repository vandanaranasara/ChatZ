from fastapi import APIRouter, HTTPException
import os

router = APIRouter(prefix="/chunk", tags=["Chunk"])

EXTRACT_DIR = "extracted_text"


def chunk_text(text, chunk_size=500, overlap=50):
    """
    Splits the text into chunks with overlap.
    chunk_size = number of characters per chunk
    overlap = number of characters that overlap between chunks
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)

        # Move pointer with overlap
        start = end - overlap  

    return chunks


@router.get("/{file_id}")
async def chunk_extracted_text(file_id: str, chunk_size: int = 500, overlap: int = 50):
    text_file = os.path.join(EXTRACT_DIR, f"{file_id}.txt")

    if not os.path.exists(text_file):
        raise HTTPException(status_code=404, detail="Extracted text not found")

    # Read extracted text
    with open(text_file, "r", encoding="utf-8") as f:
        text = f.read()

    # Run chunking
    chunks = chunk_text(text, chunk_size, overlap)

    return {
        "file_id": file_id,
        "total_chunks": len(chunks),
        "chunk_size": chunk_size,
        "overlap": overlap,
        "chunks": chunks[:5],       
        "message": "Text chunked successfully"
    }
