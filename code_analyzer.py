"""Command-line interface for the multi-language vulnerability scanner.

Usage examples (from the project root):

    # Scan the current project and print findings in a human-readable format
    python code_analyzer.py .

    # Scan another directory and output JSON
    python code_analyzer.py /path/to/other/project --format json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

from detectors.vulnerability_scanner import Vulnerability, scan_project


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simple multi-language static vulnerability scanner.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the project directory or single file to scan (default: current directory)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format for results (default: text)",
    )
    return parser.parse_args()


def print_text(findings: List[Vulnerability]) -> None:
    if not findings:
        print("No potential vulnerabilities found.")
        return

    print(f"Found {len(findings)} potential issue(s):")
    print("-" * 80)

    for vuln in findings:
        print(
            f"[{vuln.severity.upper()}] {vuln.language} {vuln.rule_id} "
            f"{vuln.file_path}:{vuln.line}"
        )
        print(f"    {vuln.description}")
        if vuln.code:
            print(f"    > {vuln.code}")
        print("-" * 80)


def print_json(findings: List[Vulnerability]) -> None:
    data = [v.to_dict() for v in findings]
    print(json.dumps(data, indent=2))


def main() -> None:
    args = parse_args()
    root = Path(args.path).expanduser().resolve()

    findings = scan_project(root)

    if args.format == "json":
        print_json(findings)
    else:
        print_text(findings)


if __name__ == "__main__":  # pragma: no cover
    main()
