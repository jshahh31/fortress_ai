# 🏰 Fortress AI

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![Clerk](https://img.shields.io/badge/Auth-Clerk-6C47FF?style=for-the-badge&logo=clerk)](https://clerk.com/)
[![ROCm](https://img.shields.io/badge/ROCm-ED1C24?style=for-the-badge&logo=amd&logoColor=white)](https://www.amd.com/en/graphics/servers-solutions-rocm)

**Fortress AI** is a private, high-performance, multi-agent legal audit system designed to run on **AMD MI300X** servers. It leverages the latest in ROCm-accelerated inference to provide a secure "Command Center" for complex legal document analysis.

---

## 🚀 Key Features

- **Unified Qwen Pipeline**: Orchestrated via LangGraph, utilizing **Qwen-3.6** for structured extraction, risk analysis, and report synthesis.
- **Hardware-Aware Design**: Optimized for ROCm 7.x and AMD MI300X clusters via vLLM.
- **High-Density RAG**: Integrated **Qdrant** vector database for multilingual legal context.
- **Enterprise Auth**: Secure user management and SSO via **Clerk**.
- **Live Streaming**: Real-time audit reports via Server-Sent Events (SSE).
- **Asynchronous Processing**: Background tasks powered by **Celery** and **Redis**.

---

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI (Async)
- **Orchestration**: LangGraph (Multi-agent DAG)
- **Inference**: vLLM (OpenAI-compatible)
- **Database**: PostgreSQL (Prisma ORM) & Qdrant (Vector DB)
- **Task Queue**: Celery & Redis

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Auth**: Clerk Next.js SDK
- **Styling**: Tailwind CSS v4 & shadcn/ui
- **Animations**: Framer Motion

---

## 📐 Architecture

The system follows a 4-node "Chain of Thought" pipeline:

1.  🔍 **Extraction Node**: Parses raw legal text into structured JSON.
2.  📚 **Research Node**: Queries the vector store for relevant precedents.
3.  ⚠️ **Risk Node**: Identifies liabilities and calculates compliance scores.
4.  📝 **Reporter Node**: Streams a final, human-readable audit report.

---

## 🚦 Getting Started

### 1. Prerequisites
- Docker & Docker Compose
- AMD MI300X GPU (for local LLM inference) or access to a vLLM endpoint.
- Clerk Account (for Auth keys)

### 2. Environment Setup
Copy `.env.template` to `.env` and fill in your keys:
```bash
cp .env.template .env
```
Key variables required:
- `CLERK_SECRET_KEY` & `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- `DATABASE_URL` (Postgres)
- `QWEN_API_BASE` (vLLM endpoint)

### 3. Launch
The entire stack is orchestrated via Docker:
```bash
docker-compose up -d
```
Access the application at `http://localhost:3000`.

---

## 🛡 License
Private / Proprietary — All rights reserved.
