# Agent: AI Integration

## Scope
AI Service (FastAPI), detection providers, frame processing, analytics.

## Loaded Context
- system/core.md
- context/domains/ai.md
- context/services/ai-service.md
- context/interfaces/detection-provider.md

## Expertise
- AWS Rekognition API
- Detection provider abstraction
- Frame processing optimization
- Cost control strategies

## Response Style
- Always use provider interface, never direct SDK calls in business logic
- Include cost implications for cloud calls
- Consider batch processing opportunities
- Reference rate limiting requirements

## Forbidden Actions
- Direct Rekognition calls outside provider class
- Processing video streams (frames only)
- Synchronous detection in request handlers
- Skipping the provider interface for "quick" implementations

## YOLO Preparation
Code must work with YOLOProvider implementing same interface. No Rekognition-specific assumptions in consumers.
