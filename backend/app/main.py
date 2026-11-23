from fastapi import FastAPI

from app.routers import admins, auth

app = FastAPI(title="Chatbot RAG UMKM")
app.include_router(auth.router)
app.include_router(admins.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
