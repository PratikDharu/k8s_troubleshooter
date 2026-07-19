import sys
from pathlib import Path

from fastapi.testclient import TestClient

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_analyze_endpoint():
    response = client.post(
        "/analyze",
        json={"text": "Warning CrashLoopBackOff Back-off restarting failed container"},
    )
    assert response.status_code == 200
    assert response.json()["problem"] == "CrashLoopBackOff"
