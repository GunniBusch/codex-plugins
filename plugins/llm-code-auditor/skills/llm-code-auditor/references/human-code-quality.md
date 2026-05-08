# Human-Quality Code Reference

Use this when a cleanup task asks for code that is readable, efficient, direct, testable, easy to inspect for bugs, and not over-engineered.

## Research Anchors

- Google Engineering Practices: code review should improve code health over time; reviewers should check design, functionality, tests, naming, comments, complexity, and context. https://google.github.io/eng-practices/review/reviewer/looking-for.html
- Google code review standard: prefer improvements that clearly improve maintainability/readability/understandability over perfection-chasing. https://google.github.io/eng-practices/review/reviewer/standard.html
- Martin Fowler: a code smell is a surface indication that often corresponds to a deeper system problem. https://martinfowler.com/bliki/CodeSmell.html
- Refactoring catalog examples: Feature Envy suggests behavior may belong near the data it uses; duplicated code and long methods are refactoring signals, not automatic proof. https://refactoring.guru/smells/feature-envy

## What Excellent Human Code Optimizes For

1. Local obviousness: a reader can see the data, invariant, and behavior in one place.
2. Domain language: names come from product concepts, protocols, schemas, UI labels, and user workflows.
3. Small public surface: fewer exported functions, fewer options, fewer states.
4. Boundary discipline: parse, validate, authorize, and sanitize at trust boundaries; internal code receives known-good shapes.
5. Negative space: unused extension points, dead config, generic wrappers, and duplicated guards are deleted.
6. Refactorability: tests pin behavior, not private structure; types make invalid states hard to express.
7. Efficient enough: choose the right algorithm and data shape before adding caches, queues, pools, or concurrency.
8. Reviewability: changes are small enough that another engineer can inspect every meaningful line.

## The Senior Refactor Loop

1. State the behavior that must remain true.
2. Identify the invariant that the current code fails to express.
3. Delete or move code until the invariant has one owner.
4. Rename after moving, because better ownership usually reveals better names.
5. Run tests. If tests are brittle, repair them to assert behavior before continuing.
6. Stop when the next change would be taste, not code health.

## Patterns To Prefer

- Direct function over single-use class.
- Concrete type over interface until there are two real implementations or a true boundary.
- Plain data plus validation at construction over optional fields checked everywhere.
- Existing framework lifecycle over custom orchestration.
- Small table/map for mechanical variation over mirrored methods.
- One cohesive module over many one-class files.
- Domain-specific duplicate code over premature generic abstraction when the cases are likely to diverge.

## Review Questions

- Can a maintainer predict all side effects from this file?
- What invariant is repeated in prose, checks, tests, and names?
- Is this layer adding mapping, validation, authorization, transactionality, caching, or observability? If not, why does it exist?
- Would a failing test point at the bug, or at a mocked implementation detail?
- Is the strictness protecting a boundary or just making future refactors expensive?
- Is this optimization solving a measured bottleneck or just making simple code harder?
