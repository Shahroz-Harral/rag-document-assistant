# 📄 RAG Document Assistant

A production-ready Retrieval-Augmented Generation (RAG) API that lets you upload documents and ask questions about them — with built-in guardrails for hallucination prevention and output validation.

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | FastAPI (Python) |
| **LLM** | Google Gemini (free tier) / Groq (fallback) |
| **RAG** | LangChain (document loaders, text splitters, retrievers) |
| **Vector Store** | Pinecone |
| **Guardrails** | Guardrails AI (output validation) |
| **Testing** | DeepEval (hallucination detection) + pytest |
| **Deployment** | Docker |

## ✨ Features

- **Document Upload** — Upload PDFs and text files, automatically chunked and embedded
- **Conversational Q&A** — Ask questions about your documents via REST API
- **Source Citations** — Every answer includes the source chunks used
- **Streaming Responses** — Real-time token streaming via SSE
- **Output Guardrails** — Validates responses for PII leaks, off-topic content, and factuality
- **Hallucination Testing** — DeepEval test suite checking faithfulness and relevancy
- **Model-Agnostic** — Swap LLM providers with one line (Gemini, Groq, OpenAI, etc.)

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Free API keys (no credit card needed):
  - [Google AI Studio](https://aistudio.google.com) — Gemini API
  - [Pinecone](https://www.pinecone.io) — Vector DB
  - [Groq](https://console.groq.com) — (optional) fast inference fallback

### Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/rag-document-assistant.git
cd rag-document-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the server
uvicorn app.main:app --reload
```

### Docker

```bash
docker build -t rag-assistant .
docker run -p 8000:8000 --env-file .env rag-assistant
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/documents/upload` | Upload and index a document |
| `GET` | `/api/documents/` | List all indexed documents |
| `POST` | `/api/chat` | Ask a question about your documents |
| `POST` | `/api/chat/stream` | Ask a question (streaming response) |
| `GET` | `/api/health` | Health check |

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Run hallucination tests (DeepEval)
deepeval test run tests/test_hallucination.py
```

## 📁 Project Structure

```
rag-document-assistant/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py             # Settings & environment config
│   ├── api/
│   │   ├── routes/
│   │   │   ├── chat.py       # Chat endpoints
│   │   │   ├── documents.py  # Document upload/listing
│   │   │   └── health.py     # Health check
│   │   └── dependencies.py   # Shared dependencies
│   ├── core/
│   │   ├── llm.py            # LLM provider setup (model-agnostic)
│   │   ├── embeddings.py     # Embedding model setup
│   │   └── guardrails.py     # Output validation rules
│   ├── services/
│   │   ├── rag.py            # RAG pipeline (chunking, retrieval, generation)
│   │   ├── document.py       # Document processing service
│   │   └── vectorstore.py    # Pinecone vector store operations
│   └── models/
│       ├── schemas.py        # Pydantic request/response models
│       └── documents.py      # Document data models
├── tests/
│   ├── test_api.py           # API endpoint tests
│   ├── test_rag.py           # RAG pipeline tests
│   └── test_hallucination.py # DeepEval hallucination tests
├── scripts/
│   └── seed_documents.py     # Script to seed sample documents
├── docs/                     # Additional documentation
├── .env.example              # Environment variable template
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 📄 License

MIT
