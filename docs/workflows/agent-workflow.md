# Agent Workflow

Canonical workflow source for agent/reviewer process. Pair with:
- `docs/workflows/reviewer-brief.md`
- `docs/workflows/reviewer-checklist.md`
- `docs/benchmarks/README.md`

## Roles

### Main agent
Responsible for:
- design
- implementation
- debugging
- UI/style updates
- commits and pushes
- user-facing progress reports

### Review agent
Responsible for:
- reviewing every pushed commit
- checking for regressions, weak assumptions, and mismatches against expected groove behavior
- reporting risks clearly and separately from the implementation agent

## Required loop for every meaningful change
1. Main agent makes a change.
2. Main agent tests locally.
3. Main agent commits and pushes.
4. Review agent reviews the pushed commit on its own side.
5. Main agent reports outcome in chat:
   - what changed
   - what tests passed
   - what reviewer found
   - what still looks risky
6. Main agent stops and asks: **approve next step**
7. No next implementation step starts until Eddie approves.

## If Eddie does not approve
- Main agent continues debugging.
- Review agent continues reviewing the current state.
- No new unrelated work starts.

## Refresh / handoff rule
When context gets too large or a clean restart is needed:
- save important state to memory/docs
- report exactly: **got to refresh**
- next session resumes from the saved workflow docs and latest repo state

## Reporting style
Reports must be plain and explicit:
- changed
- tested
- reviewer outcome
- next risk
- approval request

Avoid vague status like "should be better" without saying what was actually checked.
