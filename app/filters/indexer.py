import openai
import faiss
import numpy as np
import json
from dotenv import load_dotenv
import os

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_embedding(text):
    resp = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small"  # or "text-embedding-ada-002"
    )
    return np.array(resp.data[0].embedding, dtype=np.float32)

# 1. loads semantic blocks
with open("semantic_blocks.json", "r", encoding="utf-8") as f:
    semantic_blocks = json.load(f)

labels = list(semantic_blocks.keys())
block_texts = [
    f"{label}. {' '.join(semantic_blocks[label])}" for label in labels
]

print(block_texts)

# 2. Computes embeddings
embeddings = np.stack([get_embedding(text) for text in block_texts])

# 3. Creates FAISS index
dim = embeddings.shape[1]
index = faiss.IndexFlatL2(dim)  # Uses L2 distance
index.add(embeddings)
print(f"Indexados {len(labels)} bloques.")

# 4. Stores the index and labels
faiss.write_index(index, "blocks.index")
with open("block_labels.json", "w", encoding="utf-8") as f:
    json.dump(labels, f, ensure_ascii=False)