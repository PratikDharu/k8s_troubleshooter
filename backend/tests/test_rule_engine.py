import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.rules.engine import RuleEngine


def test_detects_image_pull_errors():
    engine = RuleEngine()
    result = engine.analyze(
        'Events: Failed to pull image "nginx:latest": rpc error: code = NotFound'
    )

    assert result["problem"] == "ImagePullBackOff"
    assert "image" in result["explanation"].lower()


def test_detects_probe_failures():
    engine = RuleEngine()
    result = engine.analyze(
        "Liveness probe failed: HTTP probe failed with statuscode: 500"
    )

    assert result["problem"] == "ProbeFailure"
    assert result["confidence"] >= 85


def test_detects_scheduling_failures():
    engine = RuleEngine()
    result = engine.analyze("0/3 nodes are available: 3 Insufficient cpu")

    assert result["problem"] == "SchedulingFailure"
    assert "schedule" in result["explanation"].lower()
