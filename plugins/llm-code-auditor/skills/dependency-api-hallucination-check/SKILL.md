---
name: dependency-api-hallucination-check
description: Use when generated code adds new dependencies, imports, packages, CLI commands, configuration keys, APIs, methods, attributes, docs examples, or framework calls that may be hallucinated, unverified, outdated, insecure, or inconsistent with the repo.
---

# Dependency API Hallucination Check

Use this skill to verify that generated code did not invent packages, methods, config, or framework behavior.

## Workflow

1. List every new dependency, import, CLI command, config key, API method, and attribute touched by the change.
2. Prefer existing repo dependencies and standard library features before adding a package.
3. Verify new package names against the official registry and lockfile. Check ownership, maintenance, popularity, license, and typosquatting/slopsquatting risk.
4. Verify API calls against installed type definitions, generated clients, official docs, or runtime introspection.
5. Remove broad `any`, reflection, dynamic lookup, or string indexing that only exists to hide uncertain object shapes.
6. Add a small compile/type/test check that proves the dependency/API surface is real.

## Red Flags

- plausible package names absent from lockfiles
- package names similar to real packages
- imports that appear only in generated code
- copied docs examples for a different library version
- config keys not read by the framework
- methods that sound natural but do not exist in types

Read `../llm-code-auditor/references/llm-failure-taxonomy.md` for hallucinated object, wrong attribute, and package-hallucination patterns.
