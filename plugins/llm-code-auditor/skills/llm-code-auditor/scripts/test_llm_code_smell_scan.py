#!/usr/bin/env python3
"""Regression tests for llm_code_smell_scan.py."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).with_name("llm_code_smell_scan.py")


def run_scan(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["python3", str(SCRIPT), *args, str(root)],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout


def test_lsp_capability_names_are_not_naming_inflation() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "server.ts").write_text(
            """
export const serverCapabilities = {
  codeActionProvider: true,
  hoverProvider: true,
  completionProvider: { resolveProvider: true },
};
""",
            encoding="utf-8",
        )

        output = run_scan(root, "--min-severity", "medium")
        assert "codeActionProvider" not in output
        assert "hoverProvider" not in output
        assert "completionProvider" not in output
        assert "naming-inflation" not in output


def test_generic_provider_name_is_still_reported() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "generated.ts").write_text(
            """
export function userProvider(data) {
  return data;
}
""",
            encoding="utf-8",
        )

        output = run_scan(root, "--min-severity", "medium")
        assert "userProvider" in output
        assert "naming-inflation" in output


def main() -> int:
    tests = [
        test_lsp_capability_names_are_not_naming_inflation,
        test_generic_provider_name_is_still_reported,
    ]
    for test in tests:
        test()
        print(f"ok {test.__name__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
