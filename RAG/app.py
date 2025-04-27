import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from faiss_index.search_faiss import search_chunks
from ctransformers import AutoModelForCausalLM
import json

# Load model
llm = AutoModelForCausalLM.from_pretrained(
    'RAG/models/llama/', 
    model_file='tinyllama-1.1b-chat-v1.0.Q2_K.gguf',
    model_type='llama',
    max_new_tokens=2048,
    context_length=8192
)

def estimate_tokens(text):
    # Quick approximation: assume 4 characters per token
    return max(1, len(text) // 4)
# Load chunk texts
CHUNK_TEXTS_DIR = "/Users/ganapathynagasubramaniam/Desktop/YabNLP/Yab-NLP-Services/faiss_index/chunk_texts.json"
with open(CHUNK_TEXTS_DIR, "r", encoding="utf-8") as f:
    chunk_texts = json.load(f)

# Build prompt
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



# Streamlit App
st.set_page_config(page_title="RAG Chatbot", page_icon="🤖", layout="wide")
st.title("💬 RAG Chatbot")

if "history" not in st.session_state:
    st.session_state.history = []

query = st.chat_input("Type your question...")

if query:
    with st.spinner("Searching and generating answer..."):
        matches = search_chunks(query, top_k=1)
        prompt = build_prompt(query, matches)
        response = llm(prompt)

    # Save to chat history
    st.session_state.history.append(("user", query))
    st.session_state.history.append(("bot", response))

# Display chat history
for role, message in st.session_state.history:
    if role == "user":
        st.chat_message("user").markdown(message)
    else:
        st.chat_message("assistant").markdown(message)
