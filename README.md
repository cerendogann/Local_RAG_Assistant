# 🧠 Offline Document Analysis Assistant (Local RAG)

An intelligent, fully offline Retrieval-Augmented Generation (RAG) assistant built with Streamlit. This system allows users to upload custom text documents, processes them into vector embeddings, and provides context-aware answers to user queries without ever connecting to an external cloud API.

## ✨ Features
* **100% Offline & Secure:** All data processing, vectorization, and LLM inference happen entirely on your local machine. Perfect for analyzing sensitive corporate data, legal contracts, and invoices.
* **Local AI Models:** Powered by `phi-3.5-mini` for text generation and `qwen3-embedding-0.6b` for semantic search via Foundry Local SDK.
* **Lightweight Vector Database:** Uses SQLite to store and query document embeddings with cosine similarity.
* **Interactive UI:** A clean, modern interface built with Streamlit, featuring real-time processing status, dynamic background themes, and direct source citation for every answer.

## 🚀 Technologies Used
* **Frontend:** Streamlit
* **AI Engine:** Foundry Local SDK
* **Database:** SQLite3
* **Language:** Python

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/cerendogann/Local_RAG_Assistant.git](https://github.com/cerendogann/Local_RAG_Assistant.git)
   cd Local_RAG_Assistant