# LLM Code Auditor

Codex plugin for detecting and fixing likely LLM-generated code quality problems.

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
