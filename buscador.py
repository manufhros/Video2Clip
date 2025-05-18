import os
import json
from dotenv import load_dotenv
import openai
import faiss
import numpy as np
from sklearn.preprocessing import normalize

# 1. Carga la API Key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 2. Utilidad para generar el embedding (conciso)
def get_embedding(text):
    resp = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small"  # O "text-embedding-ada-002"
    )
    return np.array(resp.data[0].embedding, dtype=np.float32)

# 3. Carga el índice y los labels
index = faiss.read_index("blocks.index")
with open("block_labels.json", "r", encoding="utf-8") as f:
    labels = json.load(f)

# 4. Define la función de búsqueda
def buscar_bloque(pregunta, top_k=3):
    pregunta_emb = get_embedding(pregunta).reshape(1, -1)
    # Para coseno, normaliza embeddings y usa IndexFlatIP (producto interno)
    pregunta_emb = normalize(pregunta_emb, axis=1)
    D, I = index.search(pregunta_emb, k=top_k)
    resultados = []
    for pos, (idx, score) in enumerate(zip(I[0], D[0]), 1):
        resultados.append({
            "rank": pos,
            "label": labels[idx],
            "score": float(score)
        })
    return resultados

# 5. Ejemplo de uso interactivo
if __name__ == "__main__":
    while True:
        pregunta = input("\nIntroduce tu pregunta o texto ('salir' para terminar):\n> ")
        if pregunta.strip().lower() in {"salir", "exit", "quit"}:
            break
        resultados = buscar_bloque(pregunta, top_k=3)
        print("\nResultados más similares:")
        for r in resultados:
            print(f"[{r['rank']}] {r['label']} (score: {r['score']:.4f})")