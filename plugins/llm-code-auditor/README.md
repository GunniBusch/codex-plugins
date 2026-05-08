# LLM Code Auditor

Codex plugin for detecting and fixing likely LLM-generated code quality problems. It bundles an umbrella skill plus targeted skills for focused cleanup.

The bundled skill teaches Codex to audit code for patterns such as:

- single-use abstractions
- inflated generic naming
- utility dumping
- narration comments
- pass-through layers
- speculative extensibility
- AI symmetry
- excessive defensive programming
- hallucinated APIs and attributes
- prompt-biased or incomplete code

It also includes a dependency-free heuristic scanner:

```bash
python3 plugins/llm-code-auditor/skills/llm-code-auditor/scripts/llm_code_smell_scan.py <path>
```

## Targeted Skills

- `llm-code-auditor`: umbrella audit for generated or agent-written code.
- `abstraction-pruner`: remove speculative abstractions and pass-through layers.
- `boundary-invariant-auditor`: fix redundant checks, missing boundary validation, and too-strict validation.
- `domain-readability-refactor`: improve naming, locality, comments, and domain language.
- `generated-test-auditor`: repair brittle, over-mocked, weak, or implementation-detail tests.
- `dependency-api-hallucination-check`: verify packages, imports, methods, attributes, and config.
- `performance-simplicity-auditor`: improve efficiency without fake optimization or excess machinery.
