from fastapi import FastAPI
from backend.routers import upload, extract,chunk,embed,query


app = FastAPI(title="ChatZ")

app.include_router(upload.router)
app.include_router(extract.router)
app.include_router(chunk.router)
app.include_router(embed.router)
app.include_router(query.router)