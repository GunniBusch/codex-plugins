---
name: llm-code-auditor
description: Use when asked to audit, review, clean up, de-AI, simplify, harden, or improve code that may be AI-generated, agent-written, over-engineered, redundant, brittle, too generic, too strict, too defensive, hard to read, inefficient, or likely to hide bugs.
---

# LLM Code Auditor

Use this umbrella skill to turn "plausible generated code" into code a sharp maintainer would accept. Treat LLM-ness as a hypothesis, not a verdict: prove issues from local context, tests, types, call sites, and runtime behavior.

## Quick Start

1. Inspect the changed files and surrounding call sites before editing.
2. Run the heuristic scanner when there is a local tree or file set:

```bash
python3 scripts/llm_code_smell_scan.py <path>
```

The scanner prints severity, confidence, and evidence. Treat `HIGH` as an actionable lead, `MEDIUM` as likely worth inspection, and `LOW` as a weak review signal that may be legitimate human code. Use `--min-severity medium` to hide weak leads.

3. Read `references/pattern-catalog.md`, `references/llm-failure-taxonomy.md`, or `references/human-code-quality.md` when the scanner finds issues, the code feels generated, or the task asks for a deep cleanup.
4. Fix only issues that are behavior-preserving or covered by tests. Add or adapt tests before non-trivial rewrites.
5. Prefer deleting, inlining, renaming, moving code near its use, and strengthening boundary invariants over adding new frameworks.
6. Verify with the repo's formatter, type checker, linter, and tests.

## Targeted Skills

Use the narrower skill when the task matches a specific smell family:

- `abstraction-pruner`: one-off interfaces, pass-through layers, factories, strategies, event buses, managers.
- `boundary-invariant-auditor`: redundant checks, missing boundary validation, too-strict validation, impossible states, guard clutter.
- `domain-readability-refactor`: vague naming, utility dumping, narration comments, feature envy, poor locality.
- `generated-test-auditor`: brittle LLM tests, duplicated test cases, over-mocking, implementation-detail assertions, weak assertions.
- `dependency-api-hallucination-check`: hallucinated packages, imports, methods, attributes, configuration, examples, docs.
- `performance-simplicity-auditor`: inefficient generated code, fake optimization, caches/retries/parallelism without proof.

## Audit Workflow

### 1. Map intent before judging style

Identify the domain operation, public API boundaries, persistence/network boundaries, and test surface. Do not remove an abstraction until you know whether it encodes a real boundary: external dependency, polymorphism with multiple real implementations, security boundary, transaction boundary, lifecycle boundary, or shared domain vocabulary.

### 2. Search for high-confidence generated-code patterns

Prioritize patterns that have simple fixes and low behavioral risk:

- Single-use abstraction: one interface, one implementation, one caller, wrapper forwarding unchanged arguments.
- Naming inflation: `Manager`, `Service`, `Processor`, `Handler`, `Provider`, `Factory`, `Controller`, `Engine` hiding trivial or mixed responsibilities.
- Utility dumping: `utils`, `helpers`, `common`, `shared`, `base` accumulating unrelated behavior.
- Comment narration: comments that restate the next line.
- Pass-through layers: methods that only delegate with the same arguments.
- Speculative extensibility: plugin/strategy/event/config systems with one real participant.
- AI symmetry: mechanically mirrored CRUD, equally shaped files, or repeated function skeletons where the domain needs specialization.
- Excessive defensive programming: impossible null checks, duplicated validation in every layer, `try/catch` that only logs and rethrows.
- Over-fragmentation: tiny one-class files and deep directories without a real module boundary.
- Generic abstraction language: `entity`, `item`, `object`, `data`, `info`, `processData`, `handleRequest`, `executeTask`.

### 3. Add LLM-specific correctness checks

Look beyond style. LLM-generated code often looks clean while failing at context:

- Missing corner cases: empty input, duplicate input, timezone/locale, pagination, partial failure, cancellation, concurrency, idempotency.
- Wrong input type or shape: code assumes prompt examples are exhaustive.
- Hallucinated object or attribute: API names that compile only in the model's imagination.
- Prompt-biased behavior: hard-coded sample values, demo defaults, or logic that solves the prompt but not the product.
- Incomplete generation: TODO paths, unreachable stubs, no-op catches, half-wired config, missing cleanup.
- Non-prompted consideration: extra behavior the user did not ask for, especially persistence, telemetry, network calls, broad permissions, or retries.
- Security drift: unsafe string construction, path traversal, weak auth checks, leaking secrets in logs, trusting generated input validation.
- Test drift: tests that mirror generated structure, overfit to examples, assert implementation details, or become too strict to allow safe refactoring.

### 4. Refactor toward high-quality human code

Apply these transformations:

- Collapse abstractions until the code reflects actual domain boundaries.
- Rename to domain nouns and verbs visible in product language, schema names, protocols, and user workflows.
- Move behavior to the data or module that owns the invariant.
- Replace repeated shape with a smaller data model, table-driven mapping, or one specialized path per real domain distinction.
- Centralize validation at trust boundaries; use types and constructors to make invalid states unrepresentable. Remove the 10th repeated `if` when upstream invariants already prove it.
- Prefer standard library and framework idioms already used in the repo.
- Remove comments that narrate; keep comments that explain surprising constraints, tradeoffs, protocol rules, or bug workarounds.
- Delete unused config, optionality, and extension points unless there is a second real use now.

## Guardrails

- Do not "simplify" public APIs, database schemas, migrations, serialized formats, or plugin interfaces without checking compatibility.
- Do not inline test seams, dependency injection for external services, security boundaries, or concurrency boundaries just because there is one implementation.
- Do not replace domain code with clever abstractions. High-quality code is often boring, direct, and locally obvious.
- Keep a before/after behavior proof: test, type check, static analysis, or a precise manual trace.

## Output Shape

For review-only tasks, lead with findings ordered by severity and include file/line references. For fix tasks, summarize the deleted/renamed/collapsed patterns and the verification commands run.
