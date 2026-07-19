import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.cli import main


def test_analyze_command_returns_json_output(capsys):
    exit_code = main(
        [
            "analyze",
            "--format",
            "json",
            "Warning CrashLoopBackOff Back-off restarting failed container",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0

    payload = json.loads(captured.out)
    assert payload["problem"] == "CrashLoopBackOff"
    assert payload["confidence"] >= 90
