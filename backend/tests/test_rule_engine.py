import sys
from pathlib import Path
from unittest.mock import patch

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


def test_detects_failed_mount_errors():
    engine = RuleEngine()
    result = engine.analyze(
        'MountVolume.SetUp failed for volume "cache" : failed to sync secret cache'
    )

    assert result["problem"] == "FailedMount"
    assert "mount" in result["explanation"].lower()


def test_detects_err_image_pull_errors():
    engine = RuleEngine()
    result = engine.analyze('Back-off pulling image "nginx:latest" ErrImagePull')

    assert result["problem"] == "ImagePullBackOff"
    assert "image" in result["explanation"].lower()


def test_detects_dns_resolution_failures():
    engine = RuleEngine()
    result = engine.analyze(
        "Lookup my-service.default.svc.cluster.local on 10.0.0.10:53: no such host"
    )

    assert result["problem"] == "DNSResolutionFailure"
    assert "dns" in result["explanation"].lower()


def test_detects_failed_mount_from_kubectl_events():
    engine = RuleEngine()
    result = engine.analyze(
        """Events:
  Type     Reason     Age   From               Message
  ----     ------     ----  ----               -------
  Warning  FailedMount  1m    kubelet, node-1    MountVolume.SetUp failed for volume \"cache\" : failed to sync secret cache
"""
    )

    assert result["problem"] == "FailedMount"
    assert "mount" in result["explanation"].lower()


def test_detects_scheduling_from_kubectl_events():
    engine = RuleEngine()
    result = engine.analyze(
        """Events:
  Type     Reason            Age   From                 Message
  ----     ------            ----  ----                 -------
  Warning  FailedScheduling  12s   default-scheduler    0/3 nodes are available: 3 Insufficient cpu
"""
    )

    assert result["problem"] == "SchedulingFailure"
    assert "schedule" in result["explanation"].lower()


def test_uses_llm_fallback_for_unknown_messages():
    engine = RuleEngine()

    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}, clear=False), patch(
        "app.rules.engine.requests.post"
    ) as mock_post:
        mock_post.return_value.raise_for_status.return_value = None
        mock_post.return_value.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '{"problem": "CustomFailure", "explanation": "A custom issue was detected", "confidence": 75, "commands": ["kubectl get events"]}'
                    }
                }
            ]
        }

        result = engine.analyze("some unusual kubernetes error message")

    assert result["problem"] == "CustomFailure"
    assert result["confidence"] == 75
    assert result["commands"] == ["kubectl get events"]
