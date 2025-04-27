<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9-blue.svg" alt="Python Version"/>
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License"/>
  <img src="https://img.shields.io/badge/Framework-Streamlit-orange.svg" alt="Streamlit"/>
  <img src="https://img.shields.io/badge/Database-PostgreSQL-blue.svg" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/Embeddings-MiniLM--L6--v2-red.svg" alt="Sentence Transformer"/>
  <img src="https://img.shields.io/badge/Container-Docker-blue.svg" alt="Docker"/>
</p>

# 🚀 Retrieval-Augmented Generation (RAG) Chatbot

---

## 📚 Project Overview

This project builds a **full-stack Retrieval-Augmented Generation (RAG) chatbot** that transforms raw news data into intelligent, context-aware dialogue.

> 📹 **Demo Video:** [Watch here on YouTube](https://www.youtube.com/watch?v=sDxyGaW3nSQ&ab_channel=KentNar)

---

## 🛠️ System Pipeline Overview

- **Scrape** ➔ Full-text articles + metadata from major news archives
- **Preprocess** ➔ Clean, structure, and enrich articles using modular NLP microservices
- **Chunk** ➔ Split into ~300-word paragraph chunks for fine-grained retrieval
- **Embed** ➔ Generate dense MiniLM sentence embeddings with L2 normalization
- **Index** ➔ Store vectors inside a FAISS FlatIP index for fast semantic search
- **Retrieve** ➔ Perform top-k similarity search for the most relevant paragraph chunks
- **Prompt** ➔ Construct prompts with retrieved context and feed into Tiny LLaMA
- **Generate** ➔ Output accurate, human-like responses through a Streamlit frontend

---

## 🌟 Key Features

- ✅ **Multithreaded Scraping** — fast and scalable article collection  
- ✅ **Microservices Architecture** — modular NLP pipelines (preprocessing, sentiment, summarization)  
- ✅ **Paragraph-Level Retrieval** — higher accuracy compared to article-level retrieval  
- ✅ **Local LLM Deployment** — lightweight Tiny LLaMA for offline response generation  
- ✅ **Interactive Streamlit UI** — smooth and intuitive chat experience  

---

## 📊 Technology Stack

| Component | Description |
|:----------|:------------|
| **Docker + PostgreSQL** | Database for storing scraped articles |
| **BeautifulSoup + Chromedriver** | Web scraping for clean full-text retrieval |
| **Spacy, HuggingFace Pipelines** | Preprocessing and NLP enrichment |
| **SentenceTransformers (MiniLM-L6-v2)** | Embedding generation |
| **FAISS FlatIP** | Vector indexing and similarity search |
| **Tiny LLaMA** | Lightweight LLM for response generation |
| **Streamlit** | Frontend UI for chatbot interaction |

---
