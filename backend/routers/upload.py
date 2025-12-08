from fastapi import UploadFile, File, HTTPException, APIRouter
from fastapi.responses import JSONResponse
import uuid, os, logging, fitz
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import Depends
from backend.database import SessionLocal
from backend.models import FileInfo
from backend.database import get_db

router = APIRouter(prefix="/upload", tags=["Upload"])
logger = logging.getLogger("UploadRouter")

UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload_file")
async def upload_pdf(file: UploadFile = File(...)):
    db = SessionLocal()

    file_name = file.filename  # <---- SEARCH BASED ON THIS

    # ✅ 1. Check if file already exists by file_name
    existing_file = db.query(FileInfo).filter(FileInfo.file_name == file_name).first()

    if existing_file:
        return {
            "message": "File already exists",
            "file_id": existing_file.file_id,
            "file_name": existing_file.file_name,
            "embedding_status": existing_file.embedding_status,
            "redirect_to": (
                "query"
                if existing_file.embedding_status
                else "extract"
            )
        }

    # ---------- File does NOT exist → upload normally ---------- #

    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")

    # Save file
    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(400, "Empty PDF uploaded")

    with open(file_path, "wb") as f:
        f.write(contents)

    # Extract metadata safely
    pdf = fitz.open(file_path)
    num_pages = pdf.page_count
    pdf.close()

    # Save record into DB
    new_entry = FileInfo(
        file_id=file_id,
        file_name=file_name,
        num_pages=num_pages,    
        uploaded_at=datetime.utcnow().isoformat(),
        embedding_status=False  # default
        
    )
    db.add(new_entry)
    db.commit()

    return {
        "message": "PDF uploaded successfully",
        "file_id": file_id,
        "file_name": file_name,
        "num_pages": num_pages,
        "uploaded_at": datetime.utcnow().isoformat(),
        "embedding_status": False,
        "redirect_to": "extract"
    }

@router.get("/list_files")
def list_files(db: Session = Depends(get_db)):
    files = db.query(FileInfo).all()

    return [
        {
            "file_id": f.file_id,
            "file_name": f.file_name,
            "num_pages": f.num_pages,
            "uploaded_at": f.uploaded_at,
            "embedding_status": f.embedding_status,
        }
        for f in files
    ]