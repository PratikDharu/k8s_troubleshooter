from app.container import resolve_runtime_mode


def test_server_mode_for_default_run():
    assert resolve_runtime_mode([]) == "server"


def test_cli_mode_for_analyze_command():
    assert resolve_runtime_mode(["analyze", "CrashLoopBackOff"]) == "cli"
