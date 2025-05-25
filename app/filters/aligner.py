import json

def align_blocks_to_segments(semantic_blocks: dict, segments: list) -> dict:
    segment_idx = 0
    results = {}

    # Iterates through each semantic block
    for label, block_lines in semantic_blocks.items():
        block_text = " ".join(block_lines).strip()
        block_words = block_text.split()
        n_block_words = len(block_words)
        
        # Search for the segment that contains the first word of the block
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

        # Truncate the found words to match the number of block words
        found_words = found_words[:n_block_words]

        results[label] = {
            "text": block_text,
            "start": segments[first_idx]["start"] if first_idx is not None else None,
            "end": segments[last_idx]["end"] if last_idx is not None else None,
        }

    print(json.dumps(results, indent=2, ensure_ascii=False))

    return results
