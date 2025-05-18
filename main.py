from fastapi import FastAPI, File, UploadFile, Form
from pydantic import BaseModel
import os
from uuid import uuid4
from app.pipeline import full_pipeline
from app.filters.chroma_indexer import search_blocks_in_video
from fastapi.middleware.cors import CORSMiddleware

VIDEO_DIR = "videos"
os.makedirs(VIDEO_DIR, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Para desarrollo. Limita esto en producción.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Subida y procesamiento de vídeo
@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    video_id = str(uuid4())
    filename = f"{video_id}_{file.filename}"
    file_path = os.path.join(VIDEO_DIR, filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    full_pipeline(video_id, file_path)
    print(f"Video {filename} uploaded and processed with ID: {video_id}")

    return {"message": "Video uploaded, processed and indexed successfully", "video_id": video_id, "filename": filename}


class AskRequest(BaseModel):
    video_id: str
    question: str
    top_k: int = 1


# Endpoint de consulta
@app.post("/ask")
async def ask_question(req: AskRequest):
    # Busca bloques relevantes en el vídeo usando la base de datos vectorial
    results = search_blocks_in_video(req.video_id, req.question, top_k=req.top_k)
    return {"results": results}