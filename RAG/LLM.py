# LLM.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from faiss_index.search_faiss import search_chunks
from ctransformers import AutoModelForCausalLM

llm = AutoModelForCausalLM.from_pretrained(
    'RAG/models/llama/', 
    model_file='tinyllama-1.1b-chat-v1.0.Q2_K.gguf',
    model_type='llama',
    max_new_tokens=512,
    context_length=8192
)

# Load chunk texts
CHUNK_TEXTS_DIR = "/Users/ganapathynagasubramaniam/Desktop/YabNLP/Yab-NLP-Services/faiss_index/chunk_texts.json"

# This assumes you save a dict {chunk_id: chunk_text} after building
import json
with open(CHUNK_TEXTS_DIR, "r", encoding="utf-8") as f:
    chunk_texts = json.load(f)

def build_prompt(question, matched_chunks):
    context = "\n\n".join([
        f"CONTEXT:\n{chunk_texts[chunk_id]}" for chunk_id, score in matched_chunks
    ])
    return f"""You are a helpful assistant. Use the following information to answer the question carefully.

{context}

QUESTION: {question}
ANSWER:"""

def rag_chatbot():
    print("💬 RAG Chatbot Initialized. Type 'exit' to quit.")
    while True:
        user_input = input("👤 You: ")
        if user_input.lower() == "exit":
            break

        print(f"🔍 Searching relevant paragraph chunks...")
        matches = search_chunks(user_input, top_k=15)

        if not matches:
            print("🤖 No relevant paragraphs found.")
            continue

        prompt = build_prompt(user_input, matches)
        response = llm(prompt)
        print("🤖", response)

if __name__ == "__main__":
    rag_chatbot()
