---
name: domain-readability-refactor
description: Use when code is hard to read, vague, generic, comment-heavy, utility-dumped, poorly named, over-fragmented, feature-envious, or does not use the domain language and local style of the surrounding codebase.
---

# Domain Readability Refactor

Use this skill to make code read like a domain expert wrote it.

## Workflow

1. Read surrounding code, tests, schema names, route names, UI labels, protocol docs, and logs before renaming.
2. Replace job-title names with owned domain concepts.
3. Move behavior near the data/invariant it changes most.
4. Delete narration comments; keep comments for constraints, protocol quirks, performance tradeoffs, or bug history.
5. Merge tiny files and directories when they do not represent a real module boundary.
6. Preserve strategic duplication when abstraction would erase meaning or the cases are likely to diverge.

## Naming Targets

Replace vague terms:
- `Manager`, `Service`, `Processor`, `Handler`, `Provider`, `Factory`, `Engine`
- `data`, `payload`, `item`, `entity`, `object`, `context`, `info`
- `processData`, `handleRequest`, `executeTask`, `performAction`

With names from:
- product vocabulary
- domain schemas and database tables
- protocol objects and external API docs
- user-visible workflows
- business invariants

Do not rename contractual framework/protocol names. Examples: LSP capability names such as `codeActionProvider`, `hoverProvider`, `completionProvider`, and `resolveProvider` are external vocabulary, not generic naming inflation.

When a contractual name is unclear, improve the surrounding local name instead of the contract field. For example, keep `codeActionProvider` but name the enclosing object `serverCapabilities` or `formulaEditCapabilities` if that better describes ownership.

Read `../llm-code-auditor/references/human-code-quality.md` for locality and reviewability principles.
