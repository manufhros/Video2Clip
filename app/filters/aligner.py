import json

def align_blocks_to_segments(semantic_blocks: dict, segments: list) -> dict:
    segment_idx = 0
    results = {}

    # Recorrer cada bloque temático (en orden)
    for label, block_lines in semantic_blocks.items():
        block_text = " ".join(block_lines).strip()
        block_words = block_text.split()
        n_block_words = len(block_words)
        
        # Encontrar el rango de segmentos que cubren el bloque
        found_words = []
        first_idx = None
        last_idx = None

        while segment_idx < len(segments) and len(found_words) < n_block_words:
            seg = segments[segment_idx]
            seg_words = seg['text'].split()
            if first_idx is None and seg_words:
                first_idx = segment_idx
            found_words.extend(seg_words)
            last_idx = segment_idx
            segment_idx += 1

        # Truncar extra palabras si hay un pequeño solapamiento final
        found_words = found_words[:n_block_words]

        results[label] = {
            "text": block_text,
            "start": segments[first_idx]["start"] if first_idx is not None else None,
            "end": segments[last_idx]["end"] if last_idx is not None else None,
        }

    return results
