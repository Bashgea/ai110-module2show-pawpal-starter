# PawPal+

A smart pet care scheduling assistant built with Python and Streamlit.
PawPal+ helps a busy owner plan their pet's daily care tasks — prioritising
what matters most, skipping completed work, handling recurring habits, and
warning about time conflicts — all from a clean browser UI.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Using the App](#using-the-app)
- [Smarter Scheduling](#smarter-scheduling)
- [Testing](#testing)
- [Architecture](#architecture)
- [Known Limitations](#known-limitations)

---

## Features

- Enter owner and pet info (name, species, daily time budget)
- Add one-off or recurring tasks with priority and duration
- Generate a prioritised daily schedule that fits within the owner's time budget
- View a sorted, time-ordered schedule table with per-task reasoning
- See budget usage at a glance with a progress bar
- Get plain-language warnings for budget overruns and time-window conflicts
- Recurring tasks (daily / weekly) reset themselves automatically on completion

---

## Project Structure

```
pawpal_system.py   — all domain classes and scheduling logic
app.py             — Streamlit UI (thin layer over pawpal_system)
main.py            — CLI demo script showing all features in the terminal
tests/
  test_pawpal.py   — 14 pytest tests covering sorting, recurrence, conflicts
uml.md             — Mermaid.js class diagram (reflects final implementation)
smartAlgorithm.md  — algorithmic decision notes (sorting, recurrence, budget)
phase3_plan.md     — Phase 3 feature planning notes
reflection.md      — design reflection and tradeoff writeup
requirements.txt   — Python dependencies
```

---

## Getting Started

### Prerequisites

- Python 3.10+

### Setup

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

### Run the CLI demo

```bash
python main.py
```

---

## Using the App

1. **Owner & Pet** — Enter the owner's name, available minutes for the day,
   the pet's name, and species. These are saved in session state so they
   persist while you navigate.

2. **Add a Task** — Fill in the title, duration, priority (`low / medium / high`),
   and whether it repeats (`once / daily / weekly`), then click **Add task**.
   - One-off tasks appear in the "One-off tasks" table.
   - Recurring tasks appear in the "Recurring tasks" table and show their next due date.

3. **Generate Schedule** — Click **Generate schedule** to build today's plan.
   - A progress bar shows how much of the owner's time budget is used.
   - Any budget overruns or time-window conflicts appear as warnings above the table.
   - The schedule table lists every task in chronological order with its priority
     and status.
   - Pending and completed task counts are shown as metrics at the bottom.

---

## Smarter Scheduling

### Priority-aware sorting (Algorithm A)

Tasks are sorted high → medium → low priority. Within the same priority level,
shorter tasks are scheduled first (Shortest-Job-First tie-break), so urgent
short tasks like medications are never blocked by a longer task of equal urgency.

### Status filtering

Tasks already marked complete are excluded from the next `build()` run
automatically. `Schedule.filter_by_status("pending")` returns only the
remaining work for the day.

### Recurring tasks

Tasks with `frequency="daily"` or `frequency="weekly"` reset to `"pending"`
on completion and advance their `next_due` date using Python's `timedelta`.
They reappear in every scheduled run without manual re-entry.

### Conflict detection

`ConflictDetector` runs two independent checks:

| Check | Method | Triggers when |
|---|---|---|
| Budget overrun | `check()` | Combined pet schedules exceed owner's available minutes |
| Time overlap | `detect_overlaps()` | Any two entries share overlapping time windows |

Both return plain-language warning strings shown directly in the UI.

---

## Testing

### Run the full suite

```bash
python -m pytest
```

### Run with verbose output

```bash
python -m pytest tests/test_pawpal.py -v
```

### What is tested (14 tests)

| Area | Tests | What is verified |
|---|---|---|
| Sorting | 3 | Priority order, SJF tie-break, chronological `sort_by_time()` |
| Recurrence | 5 | Daily/weekly `next_due` advancement, non-recurring regression, recurring task appears in schedule |
| Conflict detection | 4 | Budget overrun warning, clean budget, overlap detection, single-pet false-positive guard |
| Baseline | 2 | `mark_complete()` status change, `add_task()` count increase |

### Confidence level: 4 / 5

All 14 tests pass and cover the core happy paths plus key edge cases. The gap
to 5 stars is the absence of UI-layer tests, `explain()` output format tests,
and a zero-budget edge case.

---

## Architecture

The system is split into two layers:

**Data classes** (`Task`, `Pet`, `Owner`, `ScheduledEntry`) — pure data
containers defined with `@dataclass`. `Task` owns its own urgency logic
(`priority_rank()`) and recurrence logic (`mark_complete()`).

**Logic classes** (`Schedule`, `Scheduler`, `ConflictDetector`) — stateful
objects that operate on the data classes. `Scheduler.build()` merges task
sources, filters completed tasks, sorts by Algorithm A, and fits tasks into
the owner's time budget. `ConflictDetector` is a standalone checker so
conflict logic stays out of the scheduler.

See `uml.md` for the full Mermaid.js class diagram.

---

## Known Limitations

- **Single pet per schedule run** — the UI schedules one pet at a time.
  Multi-pet conflict detection is available in the backend (`main.py`) but
  not yet wired to the UI.
- **No persistent storage** — session state resets on page refresh. Tasks
  are not saved to a database or file.
- **Equal time-budget split** — when scheduling for multiple pets in code,
  the owner's minutes are divided equally (`available_minutes // n_pets`).
- **Greedy scheduler** — tasks that exceed the remaining budget are skipped
  rather than backtracked, so the schedule may not be fully packed.
