from fastapi import FastAPI, Request
from backend.routers import upload, extract ,embed ,query
from fastapi.middleware.cors import CORSMiddleware
from backend.config import setup_logging
import logging
from backend.database import engine, Base

setup_logging()
logger = logging.getLogger("MainApp")


Base.metadata.create_all(bind=engine)

app = FastAPI(title="ChatZ")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"➡️ Incoming Request: {request.method} {request.url}")

    response = await call_next(request)

    logger.info(f"⬅️ Response Status: {response.status_code}")

    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(extract.router)
app.include_router(embed.router)
app.include_router(query.router)

