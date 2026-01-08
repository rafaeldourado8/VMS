# Memory Management Rules

## What to Remember (Persistent)
- Architecture decisions
- Rejected alternatives with reasons
- Established code patterns
- API contracts between services
- Performance requirements

## What to Remember (Session)
- Current branch/feature being worked on
- Files modified in this session
- Errors encountered and solutions
- User preferences expressed

## What to Forget
- Implementation details of completed features
- Debugging steps that led nowhere
- Alternative approaches not taken
- Verbose error logs after resolution

## Session Memory Format
```yaml
session:
  feature: "feature-name"
  files_touched:
    - path/to/file.py
  decisions_made:
    - "Used X instead of Y because Z"
  open_questions:
    - "Question pending resolution"
```

## Compression Trigger
Run summarization when session context exceeds 3000 tokens.
