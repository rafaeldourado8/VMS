# Task: Code Review

## Input Required
- File(s) or diff to review
- Context (feature, bugfix, refactor)

## Review Checklist
1. Architecture compliance (check against constraints.md)
2. Domain boundary respect (no cross-domain imports)
3. Layer separation (domain -> application -> infrastructure)
4. Error handling (domain exceptions, not generic)
5. Async correctness (no blocking in async paths)
6. Test coverage (unit for domain, integration for infra)

## Output Format
```
## Summary
[One line verdict: approve/request changes]

## Issues Found
- [severity] [file:line] Description

## Suggestions
- [file:line] Improvement suggestion

## Architecture Notes
[Any patterns to reinforce or violations to fix]
```

## Severity Levels
- blocker: Breaks architecture or constraints
- major: Incorrect behavior or missing error handling
- minor: Style, naming, or minor improvements
