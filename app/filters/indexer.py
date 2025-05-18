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
        model="text-embedding-3-small"  # O "text-embedding-ada-002"
    )
    return np.array(resp.data[0].embedding, dtype=np.float32)

# 1. Carga los bloques
with open("semantic_blocks.json", "r", encoding="utf-8") as f:
    semantic_blocks = json.load(f)

labels = list(semantic_blocks.keys())
block_texts = [
    f"{label}. {' '.join(semantic_blocks[label])}" for label in labels
]

print(block_texts)

# 2. Calcula embeddings para cada bloque
embeddings = np.stack([get_embedding(text) for text in block_texts])

# 3. Crea un índice FAISS
dim = embeddings.shape[1]
index = faiss.IndexFlatL2(dim)  # Usa L2, puedes cambiar a IndexFlatIP para coseno normalizando
index.add(embeddings)
print(f"Indexados {len(labels)} bloques.")

# 4. Guarda el índice y los labels para usar luego
faiss.write_index(index, "blocks.index")
with open("block_labels.json", "w", encoding="utf-8") as f:
    json.dump(labels, f, ensure_ascii=False)