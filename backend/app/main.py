from fastapi import FastAPI

from app.api.routes import router
from app.ui import ui_page

app = FastAPI(
    title="K8sTroubleShooter",
    version="0.1.0",
    description="Kubernetes Troubleshooter",
)

app.get("/", include_in_schema=False)(ui_page)
app.include_router(router)
