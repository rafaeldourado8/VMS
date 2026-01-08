# Compression: Summarize

## Purpose
Reduce long outputs to essential information for memory storage.

## Input
Long conversation segment or code output (>2000 tokens).

## Process
1. Extract decisions made
2. Extract files created/modified
3. Extract patterns established
4. Extract open questions
5. Discard implementation details
6. Discard debugging dead ends

## Output Format
```yaml
summary:
  decisions:
    - "Decision description"
  files:
    - path/to/file.py: "What was done"
  patterns:
    - "Pattern established"
  questions:
    - "Unresolved question"
  tokens_before: N
  tokens_after: N
```

## Compression Target
Reduce to <500 tokens while preserving all decisions and file changes.
