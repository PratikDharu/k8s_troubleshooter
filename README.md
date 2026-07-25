# K8s Troubleshooter

A lightweight Kubernetes troubleshooting assistant that analyzes common Kubernetes errors and suggests likely causes and next steps.

Supports detection of issues including:

- CrashLoopBackOff
- ImagePullBackOff
- OOMKilled
- Liveness & Readiness probe failures
- Scheduling failures
- Container creation errors

---

## Quick Start (Docker)

The easiest way to use K8s Troubleshooter is with Docker.

### Run the API

```bash
docker run --rm -p 8000:8000 \
  ghcr.io/pratikdharu/k8s-troubleshooter:latest
```

Open:

- http://localhost:8000/docs

### Run the CLI

```bash
docker run --rm \
  ghcr.io/pratikdharu/k8s-troubleshooter:latest \
  analyze "Warning CrashLoopBackOff Back-off restarting failed container"
```

### Using Ollama (Optional)

Enable LLM-powered explanations using a local Ollama instance.

```bash
docker run --rm -p 8000:8000 \
  -e OLLAMA_API_BASE=http://host.docker.internal:11434/api \
  -e OLLAMA_MODEL=llama3.2 \
  ghcr.io/pratikdharu/k8s-troubleshooter:latest
```

---

## Local Development

### Requirements

- Python 3.9+

### Setup

```bash
cd backend

python3 -m venv ../.venv
source ../.venv/bin/activate

pip install -r requirements.txt
```

---

## CLI Usage

Analyze demo data:

```bash
./k8s-sense analyze --demo
```

Analyze Kubernetes output:

```bash
./k8s-sense analyze "Warning CrashLoopBackOff Back-off restarting failed container"
```

Analyze a file:

```bash
./k8s-sense analyze --file sample.txt
```

Interactive mode:

```bash
./k8s-sense analyze --interactive
```

JSON output:

```bash
./k8s-sense analyze --format json "Liveness probe failed"
```

Install the CLI globally:

```bash
./install.sh
```

Then use:

```bash
k8s-sense analyze "<kubernetes error>"
```

---

## API

Start the server:

```bash
cd backend

PYTHONPATH=. python -m uvicorn app.main:app --reload
```

Swagger UI:

http://127.0.0.1:8000/docs

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Analyze:

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"Warning CrashLoopBackOff Back-off restarting failed container"}'
```

Example response:

```json
{
  "problem": "CrashLoopBackOff",
  "confidence": 95,
  "explanation": "The container is repeatedly restarting, which usually points to an application startup failure or configuration issue.",
  "commands": [
    "kubectl logs <pod>",
    "kubectl describe pod <pod>",
    "kubectl get events"
  ]
}
```

---

## Testing

```bash
pytest backend/tests -q
```

---

## Features

- Rule-based Kubernetes diagnostics
- FastAPI REST API
- Command-line interface
- Docker image
- JSON output support
- Optional Ollama integration for richer explanations