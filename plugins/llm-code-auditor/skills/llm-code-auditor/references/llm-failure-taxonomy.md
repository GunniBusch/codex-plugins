# LLM Code Failure Taxonomy

Use this when reviewing code that looks correct at first glance but may be generated, prompt-shaped, or context-insensitive.

## Empirical LLM Failure Modes

From Tambon et al.:

- Misinterpretation: code solves a nearby task, not the intended one.
- Syntax error: generation breaks parser or build.
- Silly mistake: trivial operator/name/branch error.
- Prompt-biased code: demo values or prompt wording leak into implementation.
- Missing corner case: empty, duplicate, large, concurrent, invalid, partial, or localized input fails.
- Wrong input type: generated code assumes a shape not guaranteed by callers.
- Hallucinated object or wrong attribute: guessed APIs, fields, methods, or config.
- Incomplete generation: stubs, TODOs, no-op branches, missing cleanup.
- Non-prompted consideration: unsolicited behavior, permissions, persistence, telemetry, retries, or dependencies.

## Code Smells LLMs Commonly Drift Toward

- Symmetric boilerplate: every entity gets the same CRUD skeleton even when invariants differ.
- Generic roles: `Manager`, `Service`, `Processor`, `Handler`, `Provider`.
- Generic data words: `data`, `payload`, `item`, `entity`, `context`.
- Pass-through "architecture": controller -> service -> repository chains with unchanged arguments.
- Excess safety theater: blanket null checks, broad `try/catch`, fallback defaults that hide bugs.
- Speculative future-proofing: strategies, factories, plugins, events, options with one use.
- Narration comments: comments that restate the next statement.
- Unverified dependencies: packages/imports/commands that sound real.
- Brittle tests: tests assert mocked calls or exact generated structure rather than user-visible behavior.

## Detection Moves

- Compare code to nearby human-written code in the repo. Generated code often ignores local idioms.
- Search all callers before deleting or inlining.
- Check lockfiles and type definitions before trusting imports.
- Read tests as code, not proof. Ask whether they would fail for a real bug.
- Trace one happy path and three uncomfortable paths: empty input, invalid input, partial failure.
- Look for "why now?" for every new dependency, abstraction, cache, retry, config field, and permission.

## Fix Moves

- Replace guessed APIs with verified APIs.
- Replace prompt-shaped examples with product-shaped behavior.
- Move validation to the boundary and remove repeated internal checks.
- Collapse layers that do not add an invariant.
- Add tests for the missing uncomfortable path before changing behavior.
- Delete non-prompted features unless a real local requirement exists.
