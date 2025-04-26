# search_faiss.py
import os
import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from sklearn.preprocessing import normalize

# Load env and paths
load_dotenv()

INDEX_PATH = "/Users/ganapathynagasubramaniam/Desktop/YabNLP/Yab-NLP-Services/faiss_index/nyt_faiss_chunks.index"
MAPPING_PATH = "/Users/ganapathynagasubramaniam/Desktop/YabNLP/Yab-NLP-Services/faiss_index/chunk_mapping.json"

model = SentenceTransformer("all-MiniLM-L6-v2")

def search_chunks(query, top_k=20):
    index = faiss.read_index(INDEX_PATH)
    with open(MAPPING_PATH, "r") as f:
        id_map = json.load(f)

    query_vector = model.encode([query])
    query_vector = normalize(query_vector, norm='l2').astype("float32")

    D, I = index.search(query_vector, k=top_k)

    results = []
    for sim, idx in zip(D[0], I[0]):
        if idx == -1:
            continue
        chunk_id = id_map[str(idx)]
        results.append((chunk_id, sim))

    return results
