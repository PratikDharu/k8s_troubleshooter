import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.cli import read_text


class DummyArgs:
    def __init__(self, file=None, stdin=False, interactive=False, text=None, demo=False):
        self.file = file
        self.stdin = stdin
        self.interactive = interactive
        self.text = text
        self.demo = demo


def test_read_text_from_args_list():
    args = DummyArgs(text=["CrashLoopBackOff", "detected"])
    assert read_text(args) == "CrashLoopBackOff detected"


def test_read_text_from_file(tmp_path):
    sample = tmp_path / "sample.txt"
    sample.write_text("ImagePullBackOff observed", encoding="utf-8")
    args = DummyArgs(file=sample)
    assert read_text(args) == "ImagePullBackOff observed"


def test_read_text_from_demo_mode():
    args = DummyArgs(demo=True)
    assert read_text(args) == "Warning CrashLoopBackOff Back-off restarting failed container"
