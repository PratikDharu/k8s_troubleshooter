# k8s_troubleshooter

K8sSense is a Kubernetes troubleshooting assistant built with FastAPI and Python. The backend currently provides a structured analysis API for common Kubernetes failure patterns such as CrashLoopBackOff, ImagePullBackOff, OOMKilled, probe failures, and scheduling issues.

## Project structure

```text
backend/
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── rules/
│   ├── services/
│   └── main.py
├── tests/
├── requirements.txt
└── .env
```

## Architecture

The backend follows a simple layered design:

1. API layer: exposes HTTP endpoints
2. Service layer: coordinates analysis logic
3. Rule engine: evaluates Kubernetes diagnostic text and returns structured findings
4. Schemas: define request and response payloads

This makes it straightforward to evolve the system later with additional parsers, cluster connectors, or LLM-based explanation layers.

## Prerequisites

- Python 3.9+
- pip

## Setup

From the repository root:

```bash
cd backend
python3 -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
pip install pytest httpx
```

## Run the CLI

You can use the analyzer directly from the terminal without starting the web server:

```bash
cd backend
PYTHONPATH=. /opt/homebrew/bin/python3 -m app.cli analyze "Warning CrashLoopBackOff Back-off restarting failed container"
```

Example output:

```text
Problem: CrashLoopBackOff
Confidence: 95%

The container is repeatedly restarting, which usually points to an application startup failure or a configuration issue. Check the pod logs and recent events.

Suggested commands:
- kubectl logs <pod>
- kubectl describe pod <pod>
- kubectl get events
```

For JSON output:

```bash
cd backend
PYTHONPATH=. /opt/homebrew/bin/python3 -m app.cli analyze --format json "Liveness probe failed: HTTP probe failed with statuscode: 500"
```

## Run the API

Start the FastAPI server:

```bash
cd backend
PYTHONPATH=. /opt/homebrew/bin/python3 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Then open:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Example requests

### Health check

```bash
curl http://127.0.0.1:8000/health
```

### Analyze a Kubernetes issue

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H 'Content-Type: application/json' \
  -d '{"text":"Warning CrashLoopBackOff Back-off restarting failed container"}'
```

Example response:

```json
{
  "problem": "CrashLoopBackOff",
  "explanation": "The container is repeatedly restarting, which usually points to an application startup failure or a configuration issue. Check the pod logs and recent events.",
  "confidence": 95,
  "commands": [
    "kubectl logs <pod>",
    "kubectl describe pod <pod>",
    "kubectl get events"
  ]
}
```

## Run tests

```bash
cd /Users/pratik/Repos/k8s_troubleshooter
.venv/bin/python -m pytest backend/tests -q
```

## Next steps

The current version uses deterministic rules over diagnostic text. The next evolution can add:

- parsing of real kubectl output
- structured event extraction
- cluster connectivity and live diagnostics
- LLM-powered explanations on top of the structured analysis

