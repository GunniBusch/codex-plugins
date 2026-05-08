#!/usr/bin/env python3
"""Heuristic scanner for common LLM-generated code smells.

This is intentionally conservative and dependency-free. It finds review leads,
not proof. Codex should confirm each finding from local context before editing.
"""

from __future__ import annotations

import argparse
import ast
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".go",
    ".rb",
    ".rs",
    ".php",
    ".cs",
}

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "target",
    "__pycache__",
    ".next",
    ".turbo",
    "coverage",
}

GENERIC_SUFFIXES = (
    "Manager",
    "Service",
    "Processor",
    "Handler",
    "Provider",
    "Factory",
    "Controller",
    "Engine",
    "Coordinator",
    "Orchestrator",
    "Resolver",
    "Executor",
    "Helper",
)

GENERIC_WORDS = {
    "entity",
    "item",
    "object",
    "data",
    "info",
    "payload",
    "context",
}

EXTERNAL_PROTOCOL_NAMES = {
    # Language Server Protocol capability names. These are protocol vocabulary,
    # not naming-inflation evidence.
    "callHierarchyProvider",
    "codeActionProvider",
    "codeLensProvider",
    "colorProvider",
    "completionProvider",
    "declarationProvider",
    "definitionProvider",
    "diagnosticProvider",
    "documentFormattingProvider",
    "documentHighlightProvider",
    "documentLinkProvider",
    "documentOnTypeFormattingProvider",
    "documentRangeFormattingProvider",
    "documentSymbolProvider",
    "executeCommandProvider",
    "foldingRangeProvider",
    "hoverProvider",
    "implementationProvider",
    "inlayHintProvider",
    "inlineValueProvider",
    "linkedEditingRangeProvider",
    "monikerProvider",
    "referencesProvider",
    "renameProvider",
    "resolveProvider",
    "selectionRangeProvider",
    "semanticTokensProvider",
    "signatureHelpProvider",
    "typeDefinitionProvider",
    "typeHierarchyProvider",
    "workspaceSymbolProvider",
}

GENERIC_FUNCTION_RE = re.compile(
    r"\b(processData|handleRequest|executeTask|performAction|doStuff|handleData|processItem)\b"
)
GENERIC_SUFFIX_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*(?:" + "|".join(GENERIC_SUFFIXES) + r")\b")
GENERIC_DECLARATION_RE = re.compile(
    r"\b(class|interface|type|function|def|const|let|var|public|private|protected)\b"
)
COMMENT_RE = re.compile(r"^\s*(#|//|/\*|\*)\s*(.+?)\s*(?:\*/)?\s*$")
NARRATION_RE = re.compile(
    r"^(increment|decrement|set|get|return|check|create|update|delete|loop|iterate|initialize|assign|call)\b",
    re.IGNORECASE,
)
TRY_LOG_RETHROW_RE = re.compile(
    r"(catch\s*\([^)]*\)\s*\{[^{}]*(?:console\.(?:log|error|warn)|logger\.\w+)[^{}]*(?:throw\b)[^{}]*\})",
    re.DOTALL,
)
JS_PASS_THROUGH_RE = re.compile(
    r"\b(?:function\s+([A-Za-z_$][\w$]*)\s*\(([^)]*)\)|(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*\(([^)]*)\)\s*=>)\s*\{?\s*return\s+([A-Za-z_$][\w$.]*)\(([^)]*)\)",
    re.DOTALL,
)
LSP_CREATE_CONNECTION_RE = re.compile(r"\bcreateConnection\s*\(")
LSP_TRANSPORT_ARG_RE = re.compile(r"--(?:stdio|node-ipc|socket(?:=|\b))")

SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    code: str
    message: str
    action: str
    severity: str = "medium"
    confidence: float = 0.5
    evidence: tuple[str, ...] = ()


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan for likely LLM-generated code smells.")
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--max-findings", type=int, default=200)
    parser.add_argument(
        "--min-severity",
        choices=("low", "medium", "high"),
        default="low",
        help="Lowest severity to print. Default keeps weak review leads visible.",
    )
    args = parser.parse_args()

    files = sorted({file for path in args.paths for file in iter_code_files(path)})
    findings: list[Finding] = []
    file_texts: dict[Path, str] = {}
    for file in files:
        try:
            text = file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = file.read_text(encoding="utf-8", errors="replace")
        file_texts[file] = text
        findings.extend(scan_text(file, text))
        if file.suffix == ".py":
            findings.extend(scan_python_ast(file, text))

    findings.extend(scan_file_shape(files))
    findings.extend(scan_project_context(file_texts))
    findings = [
        finding
        for finding in findings
        if SEVERITY_ORDER[finding.severity] <= SEVERITY_ORDER[args.min_severity]
    ]
    findings = sorted(
        findings,
        key=lambda item: (SEVERITY_ORDER[item.severity], str(item.path), item.line, item.code),
    )

    for finding in findings[: args.max_findings]:
        evidence = f" Evidence: {'; '.join(finding.evidence)}" if finding.evidence else ""
        print(
            f"{finding.path}:{finding.line}: {finding.severity.upper()} "
            f"{finding.confidence:.2f} {finding.code}: {finding.message}"
            f"{evidence} Action: {finding.action}"
        )

    hidden = max(0, len(findings) - args.max_findings)
    if hidden:
        print(f"... {hidden} more findings hidden by --max-findings")

    print(f"\nScanned {len(files)} files; found {len(findings)} heuristic leads.")
    return 0


def iter_code_files(path: Path):
    if path.is_file():
        if path.suffix in CODE_EXTENSIONS:
            yield path
        return

    for child in path.rglob("*"):
        if child.is_dir():
            continue
        if any(part in SKIP_DIRS for part in child.parts):
            continue
        if child.suffix in CODE_EXTENSIONS:
            yield child


def scan_text(path: Path, text: str) -> list[Finding]:
    findings: list[Finding] = []
    lines = text.splitlines()
    basename = path.stem.lower()

    if basename in {"utils", "helpers", "common", "shared", "base", "misc", "general"}:
        findings.append(
            Finding(
                path,
                1,
                "utility-dumping",
                f"Generic module name `{path.name}` can hide unrelated behavior.",
                "Move functions near their usage or split by domain concept.",
                severity="high",
                confidence=0.85,
                evidence=("filename is a known utility-dump name",),
            )
        )

    if len(display_parts(path)) >= 8:
        findings.append(
            Finding(
                path,
                1,
                "over-fragmentation",
                "Deep path may indicate pattern-driven decomposition.",
                "Check whether directories map to real domain boundaries; merge if not.",
                severity="low",
                confidence=0.25,
                evidence=("path has at least 8 segments",),
            )
        )

    for index, line in enumerate(lines, start=1):
        for match in GENERIC_SUFFIX_RE.finditer(line):
            if is_external_protocol_name(match.group(0)):
                continue
            findings.append(
                Finding(
                    path,
                    index,
                    "naming-inflation",
                    f"Generic role name `{match.group(0)}` found.",
                    "Rename to a concrete domain noun if the role is not a real boundary.",
                    severity="medium",
                    confidence=0.6,
                    evidence=("name uses a generic architecture/job-title suffix",),
                )
            )

        if GENERIC_FUNCTION_RE.search(line) and not is_scanner_pattern_definition(line):
            findings.append(
                Finding(
                    path,
                    index,
                    "generic-abstraction-language",
                    "Generic function name found.",
                    "Rename from the domain operation or data invariant.",
                    severity="medium",
                    confidence=0.7,
                    evidence=("name matches a generated-code placeholder verb",),
                )
            )

        if GENERIC_DECLARATION_RE.search(line):
            for word in GENERIC_WORDS:
                if re.search(rf"\b{word}\b", line, flags=re.IGNORECASE):
                    findings.append(
                        Finding(
                            path,
                            index,
                            "generic-abstraction-language",
                            f"Generic term `{word}` found in a declaration/API surface.",
                            "Replace with domain language when this is not a boundary type.",
                            severity="medium",
                            confidence=0.55,
                            evidence=("generic noun appears in a declaration or API surface",),
                        )
                    )
                    break

        comment = COMMENT_RE.match(line)
        if comment and NARRATION_RE.search(comment.group(2)):
            findings.append(
                Finding(
                    path,
                    index,
                    "comment-narration",
                    "Comment appears to narrate code.",
                    "Delete unless it explains a non-obvious constraint.",
                    severity="medium",
                    confidence=0.65,
                    evidence=("comment starts with a code-action verb",),
                )
            )

    for match in TRY_LOG_RETHROW_RE.finditer(text):
        line = text.count("\n", 0, match.start()) + 1
        findings.append(
            Finding(
                path,
                line,
                "faux-robustness",
                "Catch block appears to log and rethrow without recovery.",
                "Remove it or add meaningful context/recovery.",
                severity="high",
                confidence=0.8,
                evidence=("catch block logs and rethrows",),
            )
        )

    for match in JS_PASS_THROUGH_RE.finditer(text):
        params = split_args(match.group(2) or match.group(4))
        forwarded = split_args(match.group(6))
        if params and params == forwarded:
            line = text.count("\n", 0, match.start()) + 1
            findings.append(
                Finding(
                    path,
                    line,
                    "pass-through-layer",
                    "Function forwards unchanged arguments.",
                    "Inline or move real validation/mapping into this layer.",
                    severity="high",
                    confidence=0.85,
                    evidence=("parameters and forwarded arguments match exactly",),
                )
            )

    return findings


def scan_python_ast(path: Path, text: str) -> list[Finding]:
    try:
        tree = ast.parse(text)
    except SyntaxError as error:
        return [
            Finding(
                path,
                error.lineno or 1,
                "incomplete-generation",
                f"Python syntax error: {error.msg}.",
                "Repair before deeper refactoring.",
            )
        ]

    findings: list[Finding] = []
    function_defs: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
    calls: Counter[str] = Counter()
    pass_through_lines: set[int] = set()

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            function_defs[node.name] = node
            if is_python_pass_through(node):
                pass_through_lines.add(node.lineno)
                findings.append(
                    Finding(
                        path,
                        node.lineno,
                        "pass-through-layer",
                        f"`{node.name}` forwards unchanged arguments.",
                        "Inline if no boundary, validation, or mapping is added.",
                        severity="high",
                        confidence=0.9,
                        evidence=("single return statement delegates same parameters unchanged",),
                    )
                )
        elif isinstance(node, ast.Call):
            name = called_name(node.func)
            if name:
                calls[name] += 1

    for name, node in function_defs.items():
        if name == "main" or node.lineno in pass_through_lines:
            continue
        if calls[name] == 1:
            finding = classify_single_use_function(path, name, node)
            findings.append(
                finding
            )

    return findings


def scan_project_context(file_texts: dict[Path, str]) -> list[Finding]:
    findings: list[Finding] = []
    lsp_sites = [
        (path, line_number(text, match.start()))
        for path, text in file_texts.items()
        for match in LSP_CREATE_CONNECTION_RE.finditer(text)
    ]
    if not lsp_sites:
        return findings

    has_transport_arg = any(LSP_TRANSPORT_ARG_RE.search(text) for text in file_texts.values())
    if has_transport_arg:
        return findings

    path, line = lsp_sites[0]
    findings.append(
        Finding(
            path,
            line,
            "lsp-transport-contract",
            "LSP server creates a connection, but scanned launcher code has no explicit transport argument.",
            "Verify the wrapper or package script launches the server with --stdio, --node-ipc, or --socket.",
            severity="high",
            confidence=0.8,
            evidence=("createConnection found", "no --stdio/--node-ipc/--socket found in scanned files"),
        )
    )
    return findings


def is_python_pass_through(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    body = [statement for statement in node.body if not isinstance(statement, ast.Expr) or not is_docstring(statement)]
    if len(body) != 1 or not isinstance(body[0], ast.Return):
        return False
    call = body[0].value
    if not isinstance(call, ast.Call):
        return False

    params = [arg.arg for arg in node.args.args]
    if params and params[0] in {"self", "cls"}:
        params = params[1:]
    forwarded = [arg.id for arg in call.args if isinstance(arg, ast.Name)]
    return bool(params) and params == forwarded and len(call.args) == len(params)


def classify_single_use_function(
    path: Path,
    name: str,
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> Finding:
    lowered = name.lower()
    evidence = ["called once in this file"]
    action = "Check repo-wide usage; inline if it is not a real concept."
    severity = "low"
    confidence = 0.25
    message = f"`{name}` is a single-use helper; this may be fine if the name carries a real concept."

    if name.startswith("_"):
        evidence.append("private helper")
        confidence -= 0.05

    if GENERIC_FUNCTION_RE.search(name):
        evidence.append("generic generated-style function name")
        severity = "medium"
        confidence = 0.75
        message = f"`{name}` is single-use and generically named."
    elif any(lowered.endswith(suffix.lower()) for suffix in GENERIC_SUFFIXES):
        evidence.append("generic architecture/job-title suffix")
        severity = "medium"
        confidence = 0.65
        message = f"`{name}` is single-use and uses a generic role suffix."
    elif any(word in lowered for word in GENERIC_WORDS):
        evidence.append("generic noun in helper name")
        severity = "medium"
        confidence = 0.6
        message = f"`{name}` is single-use and uses generic language."
    elif executable_statement_count(node) <= 2:
        evidence.append("tiny helper body")
        confidence = 0.35

    return Finding(
        path,
        node.lineno,
        "single-use-abstraction",
        message,
        action,
        severity=severity,
        confidence=max(0.0, min(confidence, 1.0)),
        evidence=tuple(evidence),
    )


def is_external_protocol_name(name: str) -> bool:
    return name in EXTERNAL_PROTOCOL_NAMES


def executable_statement_count(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    return sum(
        1
        for statement in node.body
        if not isinstance(statement, ast.Expr) or not is_docstring(statement)
    )


def is_scanner_pattern_definition(line: str) -> bool:
    stripped = line.strip()
    return "_RE =" in line or "GENERIC_" in line or stripped.startswith(("r\"", "r'"))


def is_docstring(statement: ast.Expr) -> bool:
    return isinstance(statement.value, ast.Constant) and isinstance(statement.value.value, str)


def called_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def split_args(raw: str) -> list[str]:
    return [part.strip() for part in raw.split(",") if part.strip()]


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def display_parts(path: Path) -> tuple[str, ...]:
    try:
        return path.relative_to(Path.cwd()).parts
    except ValueError:
        return path.parts


def scan_file_shape(files: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    by_dir: dict[Path, list[Path]] = defaultdict(list)
    for file in files:
        by_dir[file.parent].append(file)

    for directory, siblings in by_dir.items():
        if len(siblings) < 4:
            continue
        line_counts = []
        for file in siblings:
            try:
                line_counts.append((file, len(file.read_text(encoding="utf-8", errors="replace").splitlines())))
            except OSError:
                continue
        counts = Counter(count for _, count in line_counts)
        repeated = [count for count, amount in counts.items() if amount >= 3 and count > 20]
        for count in repeated:
            names = [file.name for file, line_count in line_counts if line_count == count][:5]
            findings.append(
                Finding(
                    directory,
                    1,
                    "ai-symmetry",
                    f"{len(names)} sibling files have exactly {count} lines: {', '.join(names)}.",
                    "Check for mechanically mirrored structure; consolidate or specialize.",
                )
            )

    return findings


if __name__ == "__main__":
    raise SystemExit(main())
