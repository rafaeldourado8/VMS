# Task: Debug

## Input Required
- Error message or symptom
- Affected service(s)
- Steps to reproduce (if known)

## Process
1. Classify error type (domain, infrastructure, integration)
2. Identify service boundary where error occurs
3. Trace data flow to failure point
4. Propose fix within architectural constraints
5. Suggest verification steps

## Output Format
```
## Error Classification
[Type and affected layer]

## Root Cause
[One sentence]

## Fix Location
[Service and file path]

## Fix Implementation
[Code or configuration change]

## Verification
[How to confirm fix works]
```

## Common Patterns
- MediaMTX connection: Check port 8554, RTSP URL format
- Queue issues: Check RabbitMQ connection, exchange bindings
- AI timeout: Check frame size, provider rate limits
