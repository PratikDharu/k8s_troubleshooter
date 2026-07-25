# k8s_troubleshooter

K8sTroubleshooter is a Kubernetes troubleshooting assistant built with FastAPI and Python. The backend currently provides a structured analysis API for common Kubernetes failure patterns such as CrashLoopBackOff, ImagePullBackOff, OOMKilled, probe failures, and scheduling issues.

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

The easiest way to try it is with the built-in demo input:

```bash
cd backend
./k8s-sense analyze --demo
```

That gives you an instant example result without needing to provide your own diagnostic text.

You can also analyze your own input directly from the terminal without starting the web server:

```bash
cd backend
./k8s-sense analyze "Warning CrashLoopBackOff Back-off restarting failed container"
```

You can also read input from a file or from stdin. For a friendlier experience, you can also run interactively and paste the troubleshooting text directly:

```bash
cd backend
./k8s-sense analyze --interactive
```

This is especially useful for users who are copying logs or pod diagnostics from a terminal and want a quick answer without needing to remember flags.


```bash
cd backend
PYTHONPATH=. ../.venv/bin/python -m app analyze --file ./sample.txt
```

```bash
cat ./sample.txt | PYTHONPATH=. ../.venv/bin/python -m app analyze --stdin
```

To install the executable wrapper so it is available from your shell path:

```bash
cd backend
./install.sh
```

Then run:

```bash
k8s-sense analyze "Warning CrashLoopBackOff Back-off restarting failed container"
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

## Docker for end users

Docker makes this much easier for end users because they do not need to install Python, create a virtual environment, or manage dependencies manually.

### Quick start for non-technical users

If you just want to try it quickly, run the container and paste your Kubernetes error text:

If you want the LLM fallback to work without providing API keys, run the container with a local Ollama instance reachable at http://host.docker.internal:11434 (or adjust OLLAMA_API_BASE as needed):

```bash
docker run --rm -p 8000:8000 \
  -e OLLAMA_API_BASE=http://host.docker.internal:11434/api \
  -e OLLAMA_MODEL=llama3.2 \
  ghcr.io/pratikdharu/k8s-troubleshooter:latest
```

```bash
docker run --rm -p 8000:8000 ghcr.io/pratikdharu/k8s-troubleshooter:latest
```

Then open:

- http://localhost:8000/docs

Or, if you prefer the CLI inside the container:

```bash
docker run --rm ghcr.io/pratikdharu/k8s-troubleshooter:latest analyze "Warning CrashLoopBackOff Back-off restarting failed container"
```

### Run the API in a container

From the repository root:

```bash
docker compose up --build
```

Then open:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Run the CLI inside the container

```bash
docker compose run --rm backend analyze "Warning CrashLoopBackOff Back-off restarting failed container"
```

### Where users can use the image

Because this project is hosted at https://github.com/PratikDharu/k8s_troubleshooter, the most natural place to publish the image for end users is GitHub Container Registry (GHCR).

Once the image is published there, users can run it directly with:

```bash
docker pull ghcr.io/pratikdharu/k8s_troubleshooter:latest
docker run --rm -p 8000:8000 ghcr.io/pratikdharu/k8s_troubleshooter:latest
```

That gives users a one-command experience: pull the image, run it, and use the app.

## Publish the image to GHCR

To publish the Docker image from this repository to GitHub Container Registry:

1. Push the workflow file in [.github/workflows/publish-ghcr.yml](.github/workflows/publish-ghcr.yml) to GitHub.
2. Make sure the repository has Actions enabled.
3. The workflow uses the built-in `GITHUB_TOKEN`, which already has permission to publish packages for the repository.
4. Trigger the workflow by pushing to the `main` branch or by running it manually from the Actions tab.

After the workflow completes, the image will be available as:

```bash
docker pull ghcr.io/pratikdharu/k8s_troubleshooter:latest
```

You can also build it locally with:

```bash
docker build -t k8s-troubleshooter ./backend
docker run --rm -p 8000:8000 k8s-troubleshooter
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

