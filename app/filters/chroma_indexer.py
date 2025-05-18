import chromadb
from chromadb.config import Settings
import numpy as np
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Inicializa el cliente Chroma con persistencia en disco
chroma_client = chromadb.Client(Settings(
    persist_directory="./chroma_db"
))

def get_embedding(text, model="text-embedding-3-small"):
    resp = client.embeddings.create(model=model, input=[text])
    return np.array(resp.data[0].embedding, dtype=np.float32)

def get_or_create_collection(video_id):
    return chroma_client.get_or_create_collection(name=video_id)

def safe_metadata(label, start, end):
    # Asegura que ningún campo es None
    if label is None:
        label = ""
    if start is None:
        start = 0
    if end is None:
        end = 0
    return {
        "label": label,
        "start": start,
        "end": end
    }

def index_blocks_in_collection(video_id, aligned_blocks):
    """
    Indexa todos los bloques alineados de un vídeo en su colección (por video_id)
    """
    collection = get_or_create_collection(video_id)
    ids = []
    docs = []
    embeddings = []
    metadatas = []
    for i, (label, block) in enumerate(aligned_blocks.items()):
        block_id = f"{video_id}_{i}"
        text = f"{label}. {block.get('text', '') or ''}"
        embedding = get_embedding(text)
        ids.append(block_id)
        docs.append(text)
        embeddings.append(embedding)
        metadatas.append(safe_metadata(
            label=label,
            start=block.get("start", 0),
            end=block.get("end", 0)
        ))
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=docs,
        metadatas=metadatas
    )
    print(f"✅ Indexados {len(ids)} bloques en colección {video_id}")

def search_blocks_in_video(video_id, query, top_k=2):
    """
    Busca bloques en la colección (vídeo) que sean relevantes para el query.
    """
    collection = get_or_create_collection(video_id)
    query_emb = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=top_k
    )
    blocks = []
    for i in range(len(results['ids'][0])):
        meta = results['metadatas'][0][i]
        blocks.append({
            "id": results['ids'][0][i],
            "score": results['distances'][0][i],
            "label": meta.get('label', ''),
            "start": meta.get('start', 0),
            "end": meta.get('end', 0),
            "text": results['documents'][0][i]
        })
    return blocks