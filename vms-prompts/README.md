# VMS Prompt Engineering Directory

## Structure Overview

| Directory | Purpose |
|-----------|---------|
| `system/` | Immutable system prompts. Loaded once per session. |
| `context/` | Reusable context blocks. Load only what the current task needs. |
| `memory/` | Persistent decisions and session-specific state. |
| `tasks/` | Task-specific prompt templates. One per operation type. |
| `agents/` | Specialized agent configurations for different domains. |
| `compression/` | Prompts for summarizing and extracting context from long outputs. |

## Daily Usage

### Starting a Session

```
1. Load: system/core.md (always)
2. Load: system/architecture.md (if touching infrastructure)
3. Load: relevant context/ files based on task domain
4. Load: memory/persistent/decisions.md (always)
```

### Task Execution

```
1. Identify task type (feature, debug, review, refactor, integrate)
2. Load: tasks/{task-type}.md
3. Load: relevant agent from agents/
4. Execute task
5. If output > 2000 tokens, run compression/summarize.md
```

### Session End

```
1. Run compression/extract.md on conversation
2. Update memory/session/ with extracted state
3. If permanent decision made, update memory/persistent/decisions.md
```

## Token Budget Guidelines

| Load Level | Files | Est. Tokens |
|------------|-------|-------------|
| Minimal | core.md + 1 task | ~800 |
| Standard | core.md + architecture.md + 1 domain + 1 task | ~1500 |
| Full | All system + relevant context + agent | ~2500 |

## Context Loading Rules

- Never load all context files simultaneously
- Load domain context only when working on that domain
- Infrastructure context only for devops tasks
- AI context only when touching detection/recognition

## Memory Rules

- `persistent/` = survives all sessions, edit manually
- `session/` = cleared each session, auto-generated
- Never duplicate architecture decisions in session memory

## Adding New Components

### New Domain
1. Create `context/domains/{domain}.md`
2. Update relevant agent in `agents/`
3. Add to `memory/persistent/decisions.md` if architectural

### New AI Provider (e.g., YOLO)
1. Add implementation details to `context/services/ai-service.md`
2. Update `context/interfaces/detection-provider.md`
3. No changes needed to system/ or tasks/

## File Naming

- All lowercase
- Hyphens for spaces
- `.md` extension only
- No prefixes or numbering
