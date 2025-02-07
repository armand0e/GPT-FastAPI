from fastapi import APIRouter
from sentence_transformers import SentenceTransformer

router = APIRouter()
model = SentenceTransformer("all-MiniLM-L6-v2")

@router.post("/api/sentence-embedding")
async def get_sentence_embedding(text: str):
    embeddings = model.encode([text])
    return {"embedding": embeddings.tolist()}
