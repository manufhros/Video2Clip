# V2C: Video-to-Context QA API

V2C is an application that allows you to **upload a video**, automatically transcribe and segment its content by functionality, index each semantic block in a vector database, and **ask natural language questions about the video content**. The system returns the relevant segment and its timestamps, so you can jump directly to the key moment in the video.

---

## 🚀 Features

- Automatic video upload and processing (transcription + segmentation)
- Semantic segmentation by functionality, powered by LLMs
- Per-video vector indexing (ChromaDB + OpenAI embeddings)
- Semantic search: answer questions with the relevant block, text, and timestamps
- REST API (FastAPI) for easy integration with any frontend
- Simple frontend demo (HTML/JS) to test upload and QA

---

## 🗂️ Project Structure
V2C/
│
├── app/
│   ├── filters/
│   │   ├── aligner.py
│   │   ├── chroma_indexer.py
│   │   ├── context.py
│   │   ├── segmenter.py
│   │   └── transcriber.py
│   ├── pipeline.py
│
├── main.py        # API entrypoint (FastAPI)
├── videos/        # Uploaded videos
├── chroma_db/     # Vector DB persistence
├── static/        # Frontend (index.html, style.css, etc)
└── README.md

---

## 🛠️ Requirements

- Python 3.9+
- ChromaDB
- OpenAI Python SDK
- Faster-Whisper
- FastAPI, Uvicorn
- OpenAI API key (`.env` with `OPENAI_API_KEY=...`)

**Install dependencies:**
```bash
pip install -r requirements.txt
```

---

⚡ Quickstart

1. Start the API
```bash
uvicorn main:app --reload
```

2. Open the demo frontend
```bash
python3 -m http.server 5500
```

…and open http://localhost:5500/static/index.html in your browser.

3. Workflow
	•	Upload your video (recommended: .mp4)
	•	Wait for processing (it may take a while)
	•	Ask questions about the video and get back the segment text and timestamps

4. API Endpoints

• POST /upload

Upload a video and run the whole pipeline.

Response:
```bash
{
  "message": "Video uploaded, processed and indexed successfully",
  "video_id": "...",
  "filename": "..."
}
```

• POST /ask

Semantic query by video and question.

Body:
```bash
{
  "video_id": "...",
  "question": "How do I change the document name?",
  "top_k": 1
}
```

Response:
```bash
{
  "results": [
    {
      "id": "...",
      "score": 0.04,
      "label": "Change name",
      "start": 22.5,
      "end": 27.1,
      "text": "To change the document name you should..."
    }
  ]
}
```


📦 Notes
	•	The process is slow (transcription, LLM calls, embeddings).
	•	Segmentation quality depends on the LLM and the clarity of the transcript.
	•	Only supports locally uploaded videos (not YouTube links).

⸻

👨‍💻 Authors
	•	Manuel Francisco Hidalgo Ros
@manufhros
	•	(Add more if collaborative)

⸻

📝 License

MIT License

⸻

Contributions are welcome!
Open issues or PRs for questions, improvements, or feedback.