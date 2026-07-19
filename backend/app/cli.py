import argparse
import json
import sys
from pathlib import Path

from app.rules.engine import RuleEngine


def build_parser():
    parser = argparse.ArgumentParser(
        prog="k8s-sense",
        description="Analyze Kubernetes troubleshooting text from the terminal.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze", help="Analyze a Kubernetes issue description")
    analyze_parser.add_argument("text", nargs="*", help="Text to analyze")
    analyze_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    analyze_parser.add_argument(
        "--file",
        type=Path,
        help="Read input from a file instead of the command line",
    )
    analyze_parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read input from standard input",
    )
    return parser


def format_result(result, output_format):
    if output_format == "json":
        return json.dumps(result, indent=2)

    lines = [
        f"Problem: {result['problem']}",
        f"Confidence: {result['confidence']}%",
        "",
        result["explanation"],
        "",
        "Suggested commands:",
    ]
    lines.extend(f"- {command}" for command in result["commands"])
    return "\n".join(lines)


def read_text(args):
    if args.file:
        return args.file.read_text(encoding="utf-8")

    if args.stdin:
        return sys.stdin.read()

    if args.text:
        return " ".join(args.text)

    raise ValueError("No input provided. Pass text, --file, or --stdin.")


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "analyze":
        try:
            engine = RuleEngine()
            text = read_text(args)
            result = engine.analyze(text)
            print(format_result(result, args.format))
            return 0
        except (FileNotFoundError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
