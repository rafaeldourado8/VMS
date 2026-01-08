# Compression: Extract

## Purpose
Extract structured information from conversation for session memory.

## Input
Complete conversation or conversation segment.

## Extraction Categories

### Decisions
Explicit choices between alternatives.
Format: "Chose X over Y because Z"

### Code Changes
Files created, modified, or deleted.
Format: "path/to/file: action (create/modify/delete)"

### Errors Resolved
Problems encountered and their solutions.
Format: "Error: X, Solution: Y"

### Open Items
Questions or tasks not completed.
Format: "TODO: description"

## Output Format
```yaml
extracted:
  decisions: []
  code_changes: []
  errors_resolved: []
  open_items: []
  session_duration: "HH:MM"
```

## Storage
Write output to memory/session/YYYY-MM-DD-HH-MM.yaml
