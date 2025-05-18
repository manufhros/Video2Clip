from faster_whisper import WhisperModel

def transcribe_video(video_path: str, model_size: str = "base") -> tuple[str, list, list]:
    print(f"Loading faster-whisper model '{model_size}'...")
    model = WhisperModel(model_size, compute_type="float32")

    print(f"Transcribing video: {video_path}")
    segments_gen, _ = model.transcribe(video_path, word_timestamps=True)
    segments = list(segments_gen)

    full_transcription = ""
    words_with_times = []

    for segment in segments:
        full_transcription += segment.text + " "
        if segment.words:
            for word in segment.words:
                words_with_times.append({
                    "word": word.word,
                    "start": word.start,
                    "end": word.end
                })

    transcription = full_transcription.strip()
    print("✅ Complete transcription generated.")
    return transcription, words_with_times, [
        {
            "start": segment.start,
            "end": segment.end,
            "text": segment.text,
            "words": [
                {
                    "word": word.word,
                    "start": word.start,
                    "end": word.end
                } for word in (segment.words or [])
            ]
        }
        for segment in segments
    ]