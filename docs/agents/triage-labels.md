# Triage Label Vocabulary

This project uses five canonical triage labels to classify issues and route work:

| Label | Meaning | Next action |
|-------|---------|------------|
| `needs-triage` | Issue is new and hasn't been classified | Triage agent reviews and applies role label |
| `needs-info` | Issue needs clarification before proceeding | Author adds context; author removes label when ready |
| `ready-for-agent` | Issue is ready for AI agent execution | Assign to agent workflow (implementation, spec, etc.) |
| `ready-for-human` | Issue needs human judgment or external work | Route to human reviewer; human removes label when done |
| `wontfix` | Issue will not be addressed | Close the issue; optionally archive context |

## Usage

- Issues **must** have exactly one role label (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, or `wontfix`)
- Only the active role label is present at any moment; prior labels are removed during transitions
- Triage automation (via `triage` skill) enforces these rules and coordinates transitions

## Example flow

1. **New issue** → automatically gets `needs-triage`
2. **Triaged** → label changes to `needs-info`, `ready-for-agent`, `ready-for-human`, or `wontfix`
3. **Ready** → workflow executes; issue may accumulate other metadata labels (e.g., `bug`, `feature`, `docs`)
4. **Done** → issue is closed; role label is removed

## Creating issues with pre-set labels

```bash
gh issue create --label needs-triage --title "..." --body "..."
```

To start an issue in a different state, use the appropriate label (`ready-for-agent`, etc.) when creating.
