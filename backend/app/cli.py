import argparse
import json
import sys

from app.rules.engine import RuleEngine


def build_parser():
    parser = argparse.ArgumentParser(
        prog="k8s-sense",
        description="Analyze Kubernetes troubleshooting text from the terminal.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze", help="Analyze a Kubernetes issue description")
    analyze_parser.add_argument("text", nargs="+", help="Text to analyze")
    analyze_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format",
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


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "analyze":
        engine = RuleEngine()
        text = " ".join(args.text)
        result = engine.analyze(text)
        print(format_result(result, args.format))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
