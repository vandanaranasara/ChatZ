from fastapi import APIRouter, HTTPException 
from fastapi.responses import JSONResponse
import logging
import os
import PyPDF2
from dotenv import load_dotenv
load_dotenv()

router = APIRouter(prefix="/extract", tags=["Extract"])
logger = logging.getLogger("ExtractRouter")

UPLOAD_DIR = os.getenv("UPLOAD_DIR")
EXTRACT_DIR = os.getenv("EXTRACT_DIR")
os.makedirs(EXTRACT_DIR, exist_ok=True)

@router.get("/{file_id}")
async def extract_pdf_text(file_id: str):
    logger.info(f"📥 Extract request for file_id={file_id}")
    pdf_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")

    # 1️⃣ Validate file exists
    if not os.path.exists(pdf_path):
        logger.error("❌ File not found for extraction")
        raise HTTPException(status_code=404, detail="File not found")

    extracted_path = os.path.join(EXTRACT_DIR, f"{file_id}.txt")

    # 2️⃣ Extract text using PyPDF2 
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)

            if len(reader.pages) == 0:
                logger.warning("⚠️ PDF has zero pages")
                raise HTTPException(status_code=400, detail="PDF has no pages")

            extracted_text = ""
            for page in reader.pages:
                extracted_text += page.extract_text() or ""
        logger.info(f"📝 Text extracted: {len(extracted_text)} characters")

    except PyPDF2.errors.PdfReadError:
        raise HTTPException(status_code=400, detail="PDF is encrypted or unreadable")
    except Exception as e:
        logger.exception("❌ Text extraction failed")
        raise HTTPException(status_code=500, detail=f"Error extracting text: {e}")

    # 3️⃣ Save extracted text
    with open(extracted_path, "w", encoding="utf-8") as out:
        out.write(extracted_text)
    logger.info(f"💾 Extracted text saved: {extracted_path}")

    # 4️⃣ Create preview (first lines or first 300 chars)
    preview_lines = "\n".join(extracted_text.split("\n")[:20])  # first 5 lines
    preview_chars = extracted_text[:1000]                        # first 300 chars

    preview_text = preview_lines if len(preview_lines) > 0 else preview_chars

    # 5️⃣ Return success response
    return JSONResponse(
        content={
            "message": "Text extracted successfully",
            "file_id": file_id,
            "text_file": f"{file_id}.txt",
            "text_length": len(extracted_text),
            "preview_text": preview_text.strip()  # 🆕 added preview
        }
    )

