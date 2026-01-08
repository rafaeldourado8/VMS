# Task: Refactor

## Input Required
- Target code or module
- Refactor goal (extract, simplify, optimize)

## Process
1. Identify current structure and dependencies
2. Define target structure
3. Plan incremental steps (no big bang)
4. Ensure tests exist before changing
5. Execute step by step with verification

## Output Format
```
## Current State
[Brief description of structure]

## Target State
[Brief description of goal]

## Steps
1. [Step with file changes]
2. [Step with file changes]
...

## Risk Assessment
[What could break, how to verify]
```

## Refactor Boundaries
- Never change domain models without explicit request
- Never change API contracts without versioning plan
- Never change infrastructure without migration path
