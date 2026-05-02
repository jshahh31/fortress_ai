# 🏰 Fortress AI

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-232F3E?style=for-the-badge&logo=langchain)](https://github.com/langchain-ai/langgraph)
[![ROCm](https://img.shields.io/badge/ROCm-ED1C24?style=for-the-badge&logo=amd&logoColor=white)](https://www.amd.com/en/graphics/servers-solutions-rocm)

**Fortress AI** is a private, high-performance, multi-agent legal audit system designed to run on **AMD MI300X** servers. It leverages the latest in ROCm-accelerated inference to provide a secure, air-gapped "Command Center" for complex legal document analysis.

---

## 🚀 Key Features

- **Multi-Agent Pipeline**: Orchestrated via LangGraph, utilizing specialized LLMs:
    - **Qwen 3.6 (35B)**: High-precision extraction and rigorous legal risk analysis.
    - **Gemma 4 e4b**: Deep legal research and professional report synthesis.
- **Hardware-Aware Design**: Built for ROCm 7.x, with real-time VRAM and temperature monitoring for AMD MI300X clusters.
- **High-Density RAG**: Integrated **Qdrant** vector database using `BAAI/bge-m3` embeddings for multilingual legal context.
- **Modern UI/UX**: A "Cyber-Secure Professional" dashboard built with Next.js 15, Tailwind v4, and Framer Motion.
- **Live Streaming**: Real-time audit reports via Server-Sent Events (SSE).

---

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI (Async)
- **Orchestration**: LangGraph (Multi-agent DAG)
- **Inference**: vLLM (OpenAI-compatible endpoints)
- **Database**: Qdrant (Vector DB)

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Styling**: Tailwind CSS v4 & shadcn/ui
- **Animations**: Framer Motion
- **Icons**: Lucide React

---

## 📐 Architecture

The system follows a 4-node "Chain of Thought" pipeline:

1.  🔍 **Extraction Node**: (Qwen) Parses raw legal text into structured JSON.
2.  📚 **Research Node**: (Gemma) Queries the vector store for relevant precedents.
3.  ⚠️ **Risk Node**: (Qwen) Identifies liabilities and calculates compliance scores.
4.  📝 **Reporter Node**: (Gemma) Streams a final, human-readable audit report.


## 🛡 License
Private / Proprietary — All rights reserved.
