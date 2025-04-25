import os
import argparse
import faiss
import json
import numpy as np
import psycopg2
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from sklearn.preprocessing import normalize
# Load env and paths
load_dotenv()

DB_PARAMS = dict(
    dbname="nlp_articles",
    user="nlp_user",
    password="secret",
    host="localhost",
    port=5433
)

# Output paths
INDEX_PATH = "/Users/ganapathynagasubramaniam/Desktop/YabNLP/Yab-NLP-Services/faiss_index/nyt_faiss.index"
MAPPING_PATH = "/Users/ganapathynagasubramaniam/Desktop/YabNLP/Yab-NLP-Services/faiss_index/id_mapping.json"

model = SentenceTransformer("all-MiniLM-L6-v2")

def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def query_db(article_ids):
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, headline, summary_generated, url, full_text, sentiment FROM nyt_articles WHERE id = ANY(%s);",
        (article_ids,)
    )
    results = cursor.fetchall()
    conn.close()
    return {row[0]: row for row in results}

def search(query, threshold=0.75, top_k=10):
    # Load index and mapping
    index = faiss.read_index(INDEX_PATH)
    with open(MAPPING_PATH, "r") as f:
        id_map = json.load(f)

    # Embed the query
 
    query_vector = model.encode([query])
    query_vector = normalize(query_vector, norm='l2').astype("float32")

    D, I = index.search(query_vector, k=top_k)

    matches = []
    for sim, idx in zip(D[0], I[0]):
        if idx == -1: continue  # padding index
        if sim >= threshold:
            matches.append((id_map[str(idx)], float(sim)))

    return matches

def retrieve_documents(query, threshold=0.75, top_k=2):
    matches = search(query, threshold=threshold, top_k=top_k)

    if not matches:
        return []

    article_ids = [m[0] for m in matches]
    rows = query_db(article_ids)

    documents = []
    for doc_id, score in matches:
        row = rows[doc_id]
        documents.append({
            "id": doc_id,
            "headline": row[1],
            "summary": row[2],
            "url": row[3],
            "full_text": row[4], 
            "sentiment": row[5],
            "similarity": score
        })

    return documents


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--threshold", type=float, default=0.75, help="Cosine similarity threshold")
    args = parser.parse_args()

    docs = retrieve_documents(args.query, args.threshold)
    if not docs:
        print("❌ No relevant articles found.")
    else:
        for doc in docs:
            print("\n---------------------------")
            print(f"📰 {doc['headline']}")
            print(f"📎 {doc['url']}")
            print(f"💡 Similarity: {doc['similarity']:.3f}")
            print(f"📝 {doc['summary'][:300]}...")
            print("---------------------------")
