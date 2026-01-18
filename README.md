# GeneticLLM API

A FastAPI backend service that provides a REST API for chatting with a fine-tuned genetics-focused LLM. It connects to a HuggingFace Inference Endpoint running the `genetics-llm-lora-v1` model.

## Tech Stack

- **Framework**: FastAPI 0.109
- **Server**: Uvicorn
- **HTTP Client**: httpx (async)
- **Configuration**: Pydantic Settings
- **Model Hosting**: HuggingFace Inference Endpoints
- **Containerization**: Docker
- **Orchestration**: Kubernetes (AWS EKS ready)

## Features

- **REST API Endpoints** - Chat, health checks, Swagger UI, ReDoc
- **API Key Authentication** - Supports multiple comma-separated keys, dev mode without keys
- **LLM Service** - Supports dedicated HuggingFace endpoints (TGI format) and HuggingFace Router (OpenAI-compatible)
- **Qwen2 Chat Template** - Proper prompt formatting for the fine-tuned model
- **Response Cleaning** - Removes special tokens from model output
- **180-second Timeout** - Handles cold starts on inference endpoints
- **CORS Enabled** - Configurable for production
- **Kubernetes Ready** - AWS ALB Ingress, health probes, ConfigMap/Secrets

## Quick Start

### 1. Setup Environment

```bash
# Clone and enter directory
cd genetic-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your HF_TOKEN and API_KEYS
```

### 2. Run Locally

```bash
uvicorn app.main:app --reload
```

API available at: http://localhost:8000

### 3. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Chat (with API key)
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"message": "What is CRISPR-Cas9?"}'
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chat` | Chat with the genetics LLM (requires API key) |
| GET | `/health` | Health check |
| GET | `/ready` | Readiness check |
| GET | `/docs` | Custom Swagger UI with pre-filled API key |
| GET | `/redoc` | ReDoc documentation |

### Chat Request

```json
{
  "message": "What is CRISPR-Cas9?",
  "conversation_id": "optional-id",
  "temperature": 0.7,
  "max_tokens": 512
}
```

### Chat Response

```json
{
  "response": "CRISPR-Cas9 is a revolutionary gene-editing technology...",
  "conversation_id": "abc123",
  "model": "sachinbkale27/genetics-llm-lora-merged-v1"
}
```

## Project Structure

```
genetic-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, CORS, custom Swagger UI
│   ├── config.py            # Pydantic settings from .env
│   ├── auth.py              # API key authentication
│   ├── routes/
│   │   ├── chat.py          # POST /api/v1/chat endpoint
│   │   └── health.py        # GET /health, /ready endpoints
│   ├── services/
│   │   └── llm_service.py   # HuggingFace API client (180s timeout)
│   └── models/
│       └── schemas.py       # Pydantic request/response models
├── k8s/
│   ├── configmap.yaml       # Environment config
│   ├── secret.yaml          # Sensitive credentials
│   ├── deployment.yaml      # Pod spec
│   ├── service.yaml         # ClusterIP service
│   └── ingress.yaml         # AWS ALB ingress
├── Dockerfile
├── requirements.txt
└── .env.example
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `HF_TOKEN` | HuggingFace API token | Required |
| `HF_ENDPOINT_URL` | Dedicated inference endpoint URL | Optional |
| `MODEL_NAME` | HuggingFace model ID | sachinbkale27/genetics-llm-lora-merged-v1 |
| `API_KEYS` | Comma-separated API keys | None (dev mode) |
| `MAX_NEW_TOKENS` | Max tokens to generate | 512 |
| `TEMPERATURE` | Generation temperature | 0.7 |
| `SYSTEM_PROMPT` | System prompt for genetics assistant | Configured in .env |
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |
| `LOG_LEVEL` | Logging level | info |

## Docker

### Build

```bash
docker build -t genetic-api .
```

### Run

```bash
docker run -p 8000:8000 \
  -e HF_TOKEN=your_hf_token \
  -e API_KEYS=your-api-key \
  genetic-api
```

## Kubernetes Deployment (AWS EKS)

### Prerequisites

- AWS EKS cluster
- AWS Load Balancer Controller installed
- kubectl configured

### Deploy

```bash
# Create namespace (optional)
kubectl create namespace genetic-api

# Apply manifests
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml  # Edit with real values first!
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# Check status
kubectl get pods -l app=genetic-api
kubectl get ingress genetic-api
```

### Update Secrets

```bash
# Edit secret with real values
kubectl edit secret genetic-api-secrets
```

## Related Resources

- **Frontend Chatbot**: https://github.com/sachinbkale27/genetic-chatbot
- **LLM Model**: https://huggingface.co/sachinbkale27/genetics-llm-lora-merged-v1
- **Training Dataset**: https://huggingface.co/datasets/sachinbkale27/genetics-qa
