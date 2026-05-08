---
name: generated-test-auditor
description: Use when tests may be AI-generated, brittle, duplicated, too strict, over-mocked, implementation-detail-focused, snapshot-heavy, weakly asserted, prompt-biased, or not useful for finding real bugs.
---

# Generated Test Auditor

Use this skill to turn generated tests into regression tests a maintainer can trust.

## Workflow

1. Identify the behavior each test claims to protect.
2. Check whether the test would fail for a realistic bug, not just for a refactor.
3. Remove assertions on private helpers, call order, internal data shape, exact timestamps, UUIDs, generated wording, or incidental logs unless those are the contract.
4. Collapse duplicated tests that vary only prompt examples.
5. Add uncomfortable cases: empty input, duplicates, invalid shape, boundary values, partial failure, concurrency/idempotency when relevant.
6. Prefer real collaborators or small fakes over mocks that restate the implementation.
7. Run the test suite before and after changes.

## Red Flags

- test name mirrors method name instead of behavior
- every line of implementation has a matching assertion
- snapshots cover huge blobs that reviewers cannot inspect
- mocks assert calls to private implementation details
- test data uses prompt examples only
- coverage goes up while bug-detection value stays low

Good tests are strict about observable behavior and loose about implementation. If a test blocks a good refactor while catching no real bug, fix the test.
