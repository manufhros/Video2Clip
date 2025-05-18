from app.filters.transcriber import transcribe_video
from app.filters.context import get_context
from app.filters.segmenter import segmenter
from app.filters.aligner import align_blocks_to_segments
from app.filters.chroma_indexer import index_blocks_in_collection


def transcribe(video_path: str):
    """
    Returns:
        transcription (str): The transcription text.
        words_with_times (list): List of dicts with word and timestamps.
    """
    return transcribe_video(video_path)

def extract_context(transcription: str) -> dict:
    """
    Returns:
        context (dict): Context extracted from the transcription.
    """
    return get_context(transcription)

def segment(transcription: str, context: dict) -> dict:
    """
    Returns:
        semantic_blocks (dict): {label: [texts]}
    """
    return segmenter(transcription, context)

def aligner(semantic_blocks_json: dict, words_with_times: list) -> dict:
    """
    Returns:
        aligned_blocks (dict): {label: {text, start, end}}
    """
    return align_blocks_to_segments(semantic_blocks_json, words_with_times)

def full_pipeline(video_id, video_path: str):
    # All in-memory, no temp files
    transcription, words_with_times, segments = transcribe(video_path)
    context = extract_context(transcription)
    semantic_blocks_json = segment(transcription, context)
    semantic_times_aligned = aligner(semantic_blocks_json, segments)

    # --- INDEXACIÓN EN CHROMA DB ---
    index_blocks_in_collection(video_id, semantic_times_aligned)

"""
def full_pipeline(video_id, video_path: str):
    # All in-memory, no temp files
    transcription, words_with_times, segments = transcribe(video_path)
    context = extract_context(transcription)
    semantic_blocks_json = segment(transcription, context)
    semantic_times_aligned = aligner(semantic_blocks_json, segments)

    print("\n=== TRANSCRIPCIÓN COMPLETA ===")
    print(transcription)
    print("\n=== CONTEXTO ===")
    print(json.dumps(context, indent=2, ensure_ascii=False))
    print("\n=== BLOQUES SEMÁNTICOS ===")
    print(json.dumps(semantic_blocks_json, indent=2, ensure_ascii=False))
    print("\n=== BLOQUES ALINEADOS CON TIMESTAMPS ===")
    print(json.dumps(semantic_times_aligned, indent=2, ensure_ascii=False))

    # --- INDEXACIÓN EN CHROMA DB ---
    index_blocks_in_collection(video_id, semantic_times_aligned)

    # --- EJEMPLO DE BÚSQUEDA ---
    pregunta = "¿Cómo crear un nuevo proyecto?"
    results = search_blocks_in_video(video_id, pregunta, top_k=1)
    print("\n=== RESULTADO DE BÚSQUEDA EN CHROMA DB ===")
    for block in results:
        print(json.dumps(block, indent=2, ensure_ascii=False))
        print(f"\nEste segmento va de {block['start']}s a {block['end']}s en el vídeo {video_id}.")
"""