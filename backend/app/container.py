import os
import sys
from typing import Sequence


def resolve_runtime_mode(args: Sequence[str] | None = None) -> str:
    args = list(args if args is not None else sys.argv[1:])
    if args and args[0] == "analyze":
        return "cli"
    return "server"


def main() -> int:
    mode = resolve_runtime_mode()
    if mode == "cli":
        from app.cli import main as cli_main

        return cli_main(sys.argv[2:])

    import uvicorn
    from app.main import app

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
