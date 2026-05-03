<div align="center">

# Hybrid AI Chatbot

### Local-First Intelligence with Zero API Cost

*A production-grade conversational AI system powered by local LLMs, semantic caching, and graceful offline fallback*

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black?style=flat-square)](https://ollama.ai)

</div>

---

## Overview

**Hybrid AI Chatbot** is a production-style intelligent chat system that runs **entirely on your machine** — no API keys, no cloud costs, no data leaving your device. It combines multiple local LLMs via Ollama with a semantic similarity cache, ensuring you always get a response even when models are unavailable.

The system intelligently routes queries: fast/short prompts go to a lightweight model (Phi), while complex queries are handled by a more capable model (Mistral). When both fail, a semantic cache steps in to find and return the most relevant previous answer.

---

## Features

| Category | Details |
|---|---|
| **Interface** | UI built with Streamlit |
| **LLM Runtime** | Fully local inference via Ollama — no internet required |
| **Smart Routing** | Short queries → Phi (fast) · Complex queries → Mistral (powerful) |
| **Context Memory** | Conversation-aware prompts across multi-turn chats |
| **Multi-Session** | Create, switch, and manage independent chat sessions |
| **Persistence** | Chat history saved to disk between sessions |
| **Offline Fallback** | Semantic cache returns best-match answer when models fail |
| **Message Controls** | Retry and edit previous messages |

---
**Fallback chain:**

User Input → Mistral → Phi → Semantic Cache → Response
---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit |
| **Backend** | FastAPI + Uvicorn |
| **LLM Runtime** | Ollama |
| **Models** | Mistral (primary) · Phi (fallback) |
| **Embeddings** | SentenceTransformers `all-MiniLM-L6-v2` |
| **Storage** | JSON (chat history + semantic cache) |

---

## Getting Started

### Prerequisites

- Python 3.9+
- [Ollama](https://ollama.ai) installed and running

### 1. Install dependencies

```bash
pip install fastapi uvicorn streamlit sentence-transformers requests
```

### 2. Start Ollama and pull models

```bash
# Start the Ollama server
ollama serve

# Pull both models (run in a separate terminal)
ollama pull mistral
ollama pull phi
```

### 3. Start the backend

```bash
uvicorn main:app --reload
```

API will be available at `http://localhost:8000`

### 4. Launch the UI

```bash
streamlit run ui.py
```

UI will open at `http://localhost:8501`

---

## Offline Mode

When Ollama is unavailable or both models fail to respond, the system automatically switches to **semantic cache mode**:

1. Your query is converted to a vector embedding using `all-MiniLM-L6-v2`
2. Cosine similarity is computed against all cached query-response pairs
3. The best-matching previous response is returned

This ensures the chatbot never goes completely silent — it always has something relevant to say.

---

## Roadmap

- [ ] SQLite / database integration for scalable storage
- [ ] Streaming responses from the backend
- [ ] User authentication system
- [ ] Chat export and sharing (Markdown / PDF)
- [ ] Cloud inference API fallback (OpenAI / Anthropic)
- [ ] Docker Compose for one-command setup
- [ ] RAG (Retrieval-Augmented Generation) support

---

## Author

**Sunidhi** — built for real-world AI system design

---
