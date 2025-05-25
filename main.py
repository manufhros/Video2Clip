from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
import os
from uuid import uuid4
from app.pipeline import full_pipeline
from app.filters.chroma_indexer import search_blocks_in_video
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import tempfile
import subprocess
import glob

CLIPS_DIR = "clips"
VIDEO_DIR = "videos"
os.makedirs(VIDEO_DIR, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload and process video
@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    video_id = str(uuid4())
    _, ext = os.path.splitext(file.filename)
    filename = f"{video_id}{ext}"
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

# Query endpoint
@app.post("/ask")
async def ask_question(req: AskRequest):
    results = search_blocks_in_video(req.video_id, req.question, top_k=req.top_k)
    return {"results": results}

# Download video clip
@app.get("/download_clip")
def download_clip(video_id: str, start: float, end: float):
    # Search for the video file by video_id (supports any extension)
    search_pattern = os.path.join(VIDEO_DIR, f"{video_id}.*")
    files = glob.glob(search_pattern)
    if not files:
        raise HTTPException(status_code=404, detail="Video file not found")
    input_path = files[0]
    ext = os.path.splitext(input_path)[1] or ".mp4"
    duration = end - start

    # Create a temporary file to store the clip
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmpfile:
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start),
            "-i", input_path,
            "-t", str(duration),
            "-c", "copy",
            tmpfile.name
        ]
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,  # Oculta salida estándar
            stderr=subprocess.DEVNULL   # Oculta errores
        )
        output_path = tmpfile.name
        output_filename = os.path.basename(tmpfile.name)

    # Serve the file as a response
    return FileResponse(output_path, media_type="video/mp4", filename=output_filename)