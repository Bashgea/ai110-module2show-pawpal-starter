# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

PawPal+ goes beyond a basic task list with four intelligent scheduling features:

**Priority-aware sorting (Algorithm A)**
Tasks are ordered by urgency first (high → medium → low), with shortest-duration
tasks scheduled first within the same priority level. This ensures critical care
(medications, feeding) always runs before optional enrichment activities.

**Status filtering**
Tasks already marked complete via `Task.mark_complete()` are automatically excluded
from the next scheduling run. Calling `Schedule.filter_by_status("pending")` returns
only the tasks still remaining in a given day's plan.

**Recurring tasks**
Tasks with `frequency="daily"` or `frequency="weekly"` reset themselves to `"pending"`
on completion and advance their `next_due` date by the appropriate interval using
Python's `timedelta`. This means daily medications and weekly grooming sessions
reappear automatically without manual re-entry.

**Conflict detection**
`ConflictDetector` provides two checks:
- `check()` — warns when the combined duration of all pets' schedules exceeds the
  owner's available minutes (budget overrun).
- `detect_overlaps()` — warns when any two scheduled entries share overlapping time
  windows, catching double-bookings across pets that share the same owner.

## Testing PawPal+

### Run the test suite

```bash
python -m pytest
```

To run a single file with verbose output:

```bash
python -m pytest tests/test_pawpal.py -v
```

### What the tests cover

The suite contains 14 tests across three areas:

**Sorting (3 tests)**
Verifies that `Scheduler.build()` always places high-priority tasks before
lower-priority ones, that tasks of equal priority are ordered
shortest-first (SJF tie-break), and that `sort_by_time()` returns entries
in true chronological order regardless of the order tasks were added.

**Recurrence logic (5 tests)**
Confirms that calling `mark_complete()` on a `frequency="daily"` task resets
its status to `"pending"` and advances `next_due` by exactly one day, that a
weekly task advances by seven days, that a plain non-recurring task correctly
reaches `"complete"` (regression guard), and that tasks registered via
`add_recurring_task()` appear in the built schedule.

**Conflict detection (4 tests)**
Checks that `ConflictDetector.check()` fires a budget warning when two pets'
combined schedules exceed the owner's available minutes, stays silent when they
fit, that `detect_overlaps()` catches time-window collisions when two pets share
the same start time, and produces no false positives for a single-pet schedule.

**Phase 2 baseline (2 tests)**
Original tests confirming `mark_complete()` changes task status and
`add_task()` increases a pet's task count.

### Confidence level

**4 / 5 stars**

All 14 tests pass and cover the core happy paths plus key edge cases (empty
budget, non-recurring regression, single-pet overlap). The gap to 5 stars is
that the suite does not yet test the Streamlit UI layer, the `explain()` output
format, or behaviour when `available_minutes` is 0 — edge cases noted in the
test plan but not yet implemented.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
