# Task: Integration

## Input Required
- Component to integrate (e.g., YOLO, new camera protocol)
- Integration point (which service, which interface)

## Process
1. Identify existing interface/protocol
2. Implement adapter following interface
3. Add configuration for new component
4. Register in dependency injection
5. Add feature flag if needed
6. Document in relevant context file

## Output Format
```
## Interface Used
[Protocol or abstract class]

## Adapter Implementation
[File path and key methods]

## Configuration
[Config file and keys]

## Registration
[Where and how registered]

## Testing
[How to verify integration]
```

## Integration Rules
- New providers implement existing interfaces
- No changes to consumers when adding providers
- Configuration-driven, not code-driven switching
