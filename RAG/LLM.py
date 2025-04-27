# LLM.py
import re
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from faiss_index.search_faiss import search_chunks
from ctransformers import AutoModelForCausalLM

llm = AutoModelForCausalLM.from_pretrained(
    'RAG/models/llama/', 
    model_file='tinyllama-1.1b-chat-v1.0.Q2_K.gguf',
    model_type='llama',
    max_new_tokens=2048,
    context_length=8192
)

# Load chunk texts
CHUNK_TEXTS_DIR = "/Users/ganapathynagasubramaniam/Desktop/YabNLP/Yab-NLP-Services/faiss_index/chunk_texts.json"

# This assumes you save a dict {chunk_id: chunk_text} after building
import json
with open(CHUNK_TEXTS_DIR, "r", encoding="utf-8") as f:
    chunk_texts = json.load(f)

def estimate_tokens(text):
    # Quick approximation: assume 4 characters per token
    return max(1, len(text) // 4)

def build_prompt(question, matched_chunks, max_context_tokens=8192, reserve_for_question=512):
    available_tokens = max_context_tokens - reserve_for_question
    sorted_chunks = sorted(matched_chunks, key=lambda x: -x[1]) 

    selected_texts = []
    total_tokens = 0
    for chunk_id, similarity in sorted_chunks:
        chunk_text = chunk_texts.get(chunk_id,"")
        print(chunk_text + "\n\n\n")
        if not chunk_text:
            continue
        chunk_tokens = estimate_tokens(chunk_text)
        if total_tokens + chunk_tokens > available_tokens:
            break
        selected_texts.append(chunk_text)
        total_tokens += chunk_tokens

    #context = "\n\n".join([
     #   f"CONTEXT:\n{chunk_texts[chunk_id]}" for chunk_id, score in matched_chunks
    #])
    context = "\n\n".join([f"CONTEXT:\n{c}" for c in selected_texts])
    return f"""You are a knowledgeable and concise expert assistant.

You have access to the following information extracted from multiple sources:

{context}

Based only on the information above, **synthesize a complete and clear answer to the user's question**.

You must:
- Summarize key points
- Reason logically
- Avoid copying paragraphs directly
- Use your own words to explain clearly

User's Question: {question}

Your Answer:"""

def is_incomplete(text):
    """
    Check if the generated text likely ended mid-thought.
    """
    # Simple heuristics:
    if text.strip().endswith(("...", "…", ",", "and", "or", "but")):
        return True
    if not re.search(r"[\.!\?]$", text.strip()):
        return True
    return False
def rag_chatbot():
    print("💬 RAG Chatbot Initialized. Type 'exit' to quit.")
    while True:
        user_input = input("👤 You: ")
        if user_input.lower() == "exit":
            break

        print(f"🔍 Searching relevant paragraph chunks...")
        matches = search_chunks(user_input, top_k=1)

        if not matches:
            print("🤖 No relevant paragraphs found.")
            continue

        prompt = build_prompt(user_input, matches)
        full_response = llm(prompt)
        print("🤖", full_response)
        # 2. Auto-continue if output looks incomplete
        '''max_continues = 3  # maximum times we allow continuation
        num_continues = 0

        while is_incomplete(full_response) and num_continues < max_continues:
            print("⏩ Continuing generation...")
            
            # NEW: only feed small continuation cue
            continuation_prompt = f"Continue writing from here:\n{full_response[-500:]}"
            continuation = llm(continuation_prompt)


            if not continuation.strip():  # if model generates empty, break
                break

            full_response += continuation
            print(continuation, end="")

            num_continues += 1

        print("")  # final newline'''
    print("")

if __name__ == "__main__":
    rag_chatbot()
