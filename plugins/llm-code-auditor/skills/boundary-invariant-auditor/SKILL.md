---
name: boundary-invariant-auditor
description: Use when code has too many repeated checks, guard clauses, impossible null/type checks, defensive try/catch blocks, overly strict validation, hidden invalid states, or missing validation at trust boundaries.
---

# Boundary Invariant Auditor

Use this skill to make validation strict where data is untrusted and quiet where invariants are already proven.

## Workflow

1. Mark trust boundaries: user input, network, filesystem, database, queue, environment, serialization, public API, auth/security.
2. Identify the canonical parser/schema/constructor/type that proves each invariant.
3. Remove repeated internal checks when the invariant is already guaranteed.
4. Add checks only where untrusted data enters or where persistence/concurrency can violate assumptions.
5. Replace "default and continue" behavior with explicit failure when silent fallback hides bugs.
6. Update tests to cover boundary behavior and remove brittle internal guard assertions.

## Keep vs Remove

Keep checks at:
- public API boundaries
- auth, permissions, money, file paths, commands, SQL, HTML, subprocesses
- deserialization and cross-process messages
- stale data, race-prone state, retries, idempotency

Remove or consolidate:
- same null/type/range check repeated in every helper
- catch/log/rethrow with no context or recovery
- checks impossible by type system or validated constructor
- validation that rejects future-safe values without product reason

Read `../llm-code-auditor/references/human-code-quality.md` and `../llm-code-auditor/references/llm-failure-taxonomy.md` before large rewrites.
