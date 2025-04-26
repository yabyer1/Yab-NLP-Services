# build_faiss.py
import os
import psycopg2
import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from tqdm import tqdm
from sklearn.preprocessing import normalize

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
INDEX_PATH = "/Users/ganapathynagasubramaniam/Desktop/YabNLP/Yab-NLP-Services/faiss_index/nyt_faiss_chunks.index"
MAPPING_PATH = "/Users/ganapathynagasubramaniam/Desktop/YabNLP/Yab-NLP-Services/faiss_index/chunk_mapping.json"

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

def fetch_articles():
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_text FROM nyt_articles WHERE full_text IS NOT NULL")
    rows = cursor.fetchall()
    conn.close()
    return rows

def chunk_text(text, chunk_size=300):
    # Simple way: split by paragraphs first
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current_chunk) + len(para) <= chunk_size:
            current_chunk += " " + para
        else:
            chunks.append(current_chunk.strip())
            current_chunk = para
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def build_and_save_index(articles):
    chunk_texts = []
    chunk_ids = []

    print("📦 Encoding article chunks...")
    for article_id, full_text in tqdm(articles):
        if not full_text.strip():
            continue

        chunks = chunk_text(full_text)
        for idx, chunk in enumerate(chunks):
                chunk_ids.append(f"{article_id}_{idx}")  # unique id: articleId_chunkIndex
                chunk_texts.append(chunk)

    embeddings = model.encode(chunk_texts, show_progress_bar=True)
    embeddings = normalize(embeddings, norm='l2')
    embeddings = np.array(embeddings).astype("float32")

    print("🔍 Building FAISS index...")
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    print("💾 Saving index to disk...")
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    faiss.write_index(index, INDEX_PATH)

    with open(MAPPING_PATH, "w", encoding="utf-8") as f:
        json.dump({i: chunk_ids[i] for i in range(len(chunk_ids))}, f, indent=2)
    with open("/Users/ganapathynagasubramaniam/Desktop/YabNLP/Yab-NLP-Services/faiss_index/chunk_texts.json", "w", encoding="utf-8") as f:
        json.dump({chunk_ids[i]: chunk_texts[i] for i in range(len(chunk_ids))}, f, indent=2)
    print(f"✅ Saved {len(chunk_ids)} chunks to FAISS index")

if __name__ == "__main__":
    print("🚀 Fetching articles from DB...")
    articles = fetch_articles()
    if articles:
        build_and_save_index(articles)
    else:
        print("⚠️ No articles found in DB")
