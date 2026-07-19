from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="K8sSense AI",
    version="0.1.0",
    description="AI Powered Kubernetes Troubleshooter",
)

app.include_router(router)
