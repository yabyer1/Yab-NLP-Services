import os
import psycopg2
import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from tqdm import tqdm

# Load env
load_dotenv()

# PostgreSQL connection parameters
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

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

def fetch_articles():
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_text FROM nyt_articles WHERE full_text IS NOT NULL")
    rows = cursor.fetchall()
    conn.close()
    return rows

def build_and_save_index(articles):
    ids = []
    texts = []

    print("📦 Encoding articles...")
    for article_id, text in tqdm(articles):
        if len(text.strip()) > 30:
            ids.append(article_id)
            texts.append(text)

    embeddings = model.encode(texts, show_progress_bar=True)
    embeddings = np.array(embeddings).astype("float32")

    print("🔍 Building FAISS index...")
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    print("💾 Saving index to disk...")
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    faiss.write_index(index, INDEX_PATH)

    id_map = {i: ids[i] for i in range(len(ids))}
    with open(MAPPING_PATH, "w", encoding="utf-8") as f:
        json.dump(id_map, f, indent=2)

    print(f"✅ Saved {len(ids)} vectors to FAISS index")

if __name__ == "__main__":
    print("🚀 Fetching articles from DB...")
    articles = fetch_articles()
    if articles:
        build_and_save_index(articles)
    else:
        print("⚠️ No articles found in DB")
