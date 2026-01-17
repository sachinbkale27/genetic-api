# GeneticLLM API

FastAPI backend for chatting with the genetics-llm-lora-v1 model via HuggingFace Inference API.

## Features

- REST API for genetics Q&A
- API key authentication
- HuggingFace Inference API integration
- Kubernetes-ready with AWS ALB support
- Docker containerization

## Quick Start

### 1. Setup Environment

```bash
# Clone and enter directory
cd genetic-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

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
| GET | `/health` | Health check |
| GET | `/ready` | Readiness check |
| POST | `/api/v1/chat` | Chat with the genetics LLM |
| GET | `/docs` | Swagger UI documentation |
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
  "model": "sachinbkale27/genetics-llm-lora-v1"
}
```

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

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `HF_TOKEN` | HuggingFace API token | Required |
| `API_KEYS` | Comma-separated API keys | None (dev mode) |
| `MODEL_NAME` | HuggingFace model ID | sachinbkale27/genetics-llm-lora-merged-v1 |
| `MAX_NEW_TOKENS` | Max tokens to generate | 512 |
| `TEMPERATURE` | Generation temperature | 0.7 |
| `LOG_LEVEL` | Logging level | info |

## Project Structure

```
genetic-api/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app
│   ├── config.py         # Settings
│   ├── auth.py           # API key auth
│   ├── routes/
│   │   ├── chat.py       # Chat endpoint
│   │   └── health.py     # Health checks
│   ├── services/
│   │   └── llm_service.py  # HF client
│   └── models/
│       └── schemas.py    # Pydantic models
├── k8s/
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ingress.yaml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Links

- **Model**: https://huggingface.co/sachinbkale27/genetics-llm-lora-merged-v1
- **Dataset**: https://huggingface.co/datasets/sachinbkale27/genetics-qa
