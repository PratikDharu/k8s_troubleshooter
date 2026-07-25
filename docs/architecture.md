# Architecture

## Project Structure

backend/
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── rules/
│   ├── services/
│   └── main.py

## Layers

1. API
2. Services
3. Rule Engine
4. Models

The application uses deterministic rules to classify Kubernetes issues before optionally falling back to an LLM for richer explanations.