from fastapi import FastAPI, File, UploadFile, Form
from pydantic import BaseModel
import os
from uuid import uuid4

app = FastAPI()

VIDEO_DIR = "videos"
os.makedirs(VIDEO_DIR, exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Hello World"}



@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    # Genera un ID único para el vídeo
    video_id = str(uuid4())
    filename = f"{video_id}_{file.filename}"
    file_path = os.path.join(VIDEO_DIR, filename)
    # Guarda el archivo físicamente
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    # Puedes guardar el mapping video_id -> file_path en una BD o un JSON si quieres.
    return {"message": "Video uploaded successfully", "video_id": video_id, "filename": filename}

class AskRequest(BaseModel):
    video_id: str
    question: str

@app.post("/ask")
async def ask_question(req: AskRequest):
    """
    Endpoint to ask a question about the uploaded video.
    Returns the answer, timestamps and the block label.
    """
    # Aquí iría la lógica real de búsqueda, pero de momento dummy:
    return {
        "answer": "Texto de respuesta generada",
        "start": 41.3,
        "end": 48.1,
        "block": "Crear proyecto"
    }