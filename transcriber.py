from pathlib import Path
from faster_whisper import WhisperModel
import json

def transcribe_video(video_path: str, model_size: str = "base") -> tuple[str, str]:
    print(f"Loading faster-whisper model '{model_size}'...")
    model = WhisperModel(model_size, compute_type="float32")

    print(f"Transcribing video: {video_path}")
    segments_gen, _ = model.transcribe(video_path, word_timestamps=True)
    segments = list(segments_gen)

    # Guardar segmentos y transcripción completa
    segments_data = []
    full_transcription = ""
    for segment in segments:
        segments_data.append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text,
            "words": [
                {"word": w.word, "start": w.start, "end": w.end}
                for w in (segment.words or [])
            ]
        })
        full_transcription += segment.text + " "

    with open("whisper_segments.json", "w", encoding="utf-8") as f:
        json.dump(segments_data, f, indent=2, ensure_ascii=False)

    with open("transcription.txt", "w", encoding="utf-8") as f:
        f.write(full_transcription.strip())

    print("✅ Segmentos con timestamps guardados en whisper_segments.json")
    print("✅ Transcripción completa guardada en transcription.txt")
    return "transcription.txt", "whisper_segments.json"

if __name__ == "__main__":
    transcribe_video("./videos/custom1.mp4", model_size="base")