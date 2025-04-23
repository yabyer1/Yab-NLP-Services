import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from faiss_index.search_faiss import retrieve_documents
results = retrieve_documents("Why is inflation rising?", threshold=0.75)
from ctransformers import AutoModelForCausalLM
for doc in results:
    print(doc['headline'], doc['similarity'])

from transformers import pipeline

llm = AutoModelForCausalLM.from_pretrained(
    'RAG/models/llama/',  # local directory
    model_file='tinyllama-1.1b-chat-v1.0.Q2_K.gguf',
    model_type='llama',
    max_new_tokens=512,         # control output size
    context_length=8192         # ✅ max context size supported
)

def is_reference_question(message):
        keywords = ["why", "how", "what", "who", "when", "impact", "effect", "cause", "change", "should"]
        return any(kw in message.lower() for kw in keywords) #return true if we havea  reference question and need to ujse extra context

def build_rag_prompt(question, retrieved_articles):
    
    context = "\n\n".join([
        f"TITLE: {a['headline']}\nSUMMARY: {a['summary']}\nTEXT: {a['full_text'][:800]}"
      
        for a in retrieved_articles
    ])
    return f"""You are a helpful assistant. Use the following articles to answer the question:

{context}

QUESTION: {question}
ANSWER:"""


def rag_chatbot():
    print("💬 RAG Chatbot Initialized. Type 'exit' to quit.")
    while True:
        user_input = input("👤 You: ")
        if user_input.lower() == "exit":
            break

        if is_reference_question(user_input):
            print("🔍 Triggering semantic search...")
            matches = retrieve_documents(user_input, threshold=0.5)
            if not matches:
                print("🤖 No relevant articles found.")
                continue
            

       
            prompt = build_rag_prompt(user_input, matches)
            response = llm(prompt)
            print("🤖", response)

        else:
            print("🤖 I'm here to help with news-related questions. Ask me something!")
if __name__ == "__main__":
    rag_chatbot()