# PawPal+ Project Reflection

## App Screenshot

<a href="/course_images/ai110/pawpal_screenshot.png" target="_blank"><img src='/course_images/ai110/pawpal_screenshot.png' alt='PawPal+ app screenshot' width='600'/></a>



## 1. System Design

**a. Initial design**

The initial design has six classes organized into two layers: data classes and logic classes.

**Data classes** (use Python `@dataclass` for clean attribute definitions):
- `Task` — represents a single care activity. Holds `title`, `duration_minutes`, `priority`, and `description`. Responsible for knowing its own urgency via `priority_rank()`.
- `Pet` — represents the animal being cared for. Holds `name`, `species`, `age`, and `special_needs`. Responsible for providing species-appropriate default tasks via `get_default_tasks()`.
- `Owner` — represents the person managing care. Holds `name`, `available_minutes` (daily time budget), and `preferred_start_time`. No behavior — purely a data container passed to the scheduler.
- `ScheduledEntry` — a thin wrapper that pairs a `Task` with a computed `start_time`, `end_time`, and a `reason` string explaining why it was included. Exists so the timeline is explicit rather than stored as raw tuples.

**Logic classes:**
- `Schedule` — the output of the planning process. Owns an ordered list of `ScheduledEntry` objects and tracks `total_duration`. Responsible for checking feasibility against the owner's time budget and producing a human-readable explanation of the plan.
- `Scheduler` — the planning engine. Takes an `Owner`, a `Pet`, and a list of candidate `Task`s, then produces a `Schedule` via `build()`. Responsible for sorting by priority and fitting tasks within the available time window.

**b. Design changes**

Yes, four changes were made after reviewing the initial design for missing relationships and logic bottlenecks:

1. **`Schedule` now owns `Owner` and `Pet`.** The original design passed `owner` as an argument to `is_feasible(owner)` and had no reference to `Pet`. Storing both at construction time makes `Schedule` self-contained — `is_feasible()` needs no arguments, and `explain()` can produce context like "Jordan's plan for Mochi" without any extra input.

2. **`Scheduler.build()` merges `pet.get_default_tasks()` internally.** The initial design left no clear path for pet defaults to enter the schedule. Moving the merge into `build()` keeps `app.py` simple — the caller only supplies manually-added tasks and the scheduler handles defaults transparently.

3. **Time arithmetic uses `datetime` internally.** `start_time` and `end_time` are stored as display strings (`"08:00"`), but computing them requires real arithmetic. `build()` now works with `datetime` objects and converts to strings only at the point of creating a `ScheduledEntry`, avoiding string-manipulation bugs at the time boundary.

4. **Budget is checked inside `build()` before each entry is added.** The original structure would have allowed `build()` to produce an over-budget `Schedule` and only detect it afterward via `is_feasible()`. The revised approach skips any task that exceeds remaining time, so the returned `Schedule` is always feasible by construction.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints:

1. **Time budget** — `Owner.available_minutes` is the hard ceiling. No schedule is ever returned that exceeds it; tasks are skipped rather than allowed to overflow.
2. **Priority** — tasks are ranked high (3) → medium (2) → low (1). High-priority tasks always enter the schedule before lower-priority ones, regardless of duration.
3. **Owner preference** — `preferred_start_time` anchors the timeline. All time arithmetic flows forward from that value, so the schedule always reflects when the owner actually starts their day.

Priority was decided as the most important constraint because the scenario is pet care: missing a medication is worse than missing a grooming session. Time budget is a hard constraint rather than a soft one because producing an over-budget schedule would be misleading — the owner has a fixed amount of time and the plan must fit it.

**b. Tradeoffs**

The scheduler skips any task whose `duration_minutes` exceeds the remaining time budget rather than attempting to fit shorter tasks around it. For example, if 15 minutes remain and the next high-priority task takes 20 minutes, that task is dropped entirely — even if a 10-minute medium-priority task could still fit in the gap.

This is a greedy approach: it processes tasks in sorted order and makes a permanent skip decision without backtracking. A more optimal algorithm (e.g., a knapsack-style search) could fill that 15-minute gap with the best-fitting lower-priority task, producing a fuller schedule.

The tradeoff is reasonable here because pet care tasks have a strict urgency ordering — it would be wrong to schedule a grooming session in the slot where a vet medication was skipped just because grooming is shorter. Simplicity and predictability ("high-priority tasks are always attempted first, in full") matter more than packing every minute, and the approach runs in O(n log n) time regardless of task count.

---

## 3. AI Collaboration

**a. How you used AI**

This project was built using **Claude Code** (Anthropic's CLI tool) rather than VS Code Copilot. Claude Code was active throughout every phase as a conversational coding partner in the terminal.

The most effective uses were:

- **Design brainstorming** — asking Claude to compare two sorting algorithms (priority+SJF vs. weighted score) before writing a single line. Having the trade-offs written out in `smartAlgorithm.md` meant the implementation decision was already made when coding started, rather than discovered mid-build.
- **Incremental implementation** — asking Claude to add one feature at a time (e.g., "add `recurring_tasks` to `Pet` and wire it into `Scheduler.build()`") kept changes small and reviewable. Each edit was read before being accepted.
- **Test generation** — describing the test plan in plain English ("verify a daily task stays pending after mark_complete") and having Claude produce the pytest code, which was then read and verified against the actual method signatures before running.
- **Documentation passes** — using Claude to draft docstrings and README sections, then editing them for accuracy and tone.

The most helpful prompt pattern was giving context before asking: "here is what the method currently does — now add X" produced much more targeted edits than open-ended requests.

**b. Judgment and verification**

One clear moment of not accepting a suggestion as-is: Claude's initial `mark_complete()` implementation for recurring tasks set `status = "complete"` and then immediately reset it to `"pending"` in two separate lines, with the `"complete"` state lasting only a microsecond. The suggestion was technically correct — the task would always re-appear in the next run — but it made the method's intent impossible to read at a glance, and it would have broken the existing `test_mark_complete_changes_status` test, which asserts `status == "complete"` after the call.

The fix was to read the test first, confirm what contract the method was already expected to uphold for non-recurring tasks, then clarify to Claude that the reset should only apply when `frequency` is set. The revised version handles both cases cleanly with a single dict lookup, and the regression test continues to pass.

---

## 4. Testing and Verification

**a. What you tested**

The 14-test suite covers three core behaviors:

- **Sorting** — that priority order is respected, that SJF tie-breaking works within a priority level, and that `sort_by_time()` returns entries chronologically regardless of how tasks were added.
- **Recurrence** — that `mark_complete()` advances `next_due` correctly for daily and weekly tasks, that status resets to `"pending"` only for recurring tasks, and that a task registered with `add_recurring_task()` actually appears in the built schedule.
- **Conflict detection** — that budget overruns trigger a warning, that clean budgets do not, that two pets starting at the same time produce overlap warnings, and that a single pet's schedule never falsely flags itself.

These tests matter because they verify the three features that differentiate PawPal+ from a static list: intelligent ordering, automatic recurrence, and multi-pet safety.

**b. Confidence**

**4 / 5.** The happy paths and most edge cases are covered and all 14 tests pass. The remaining uncertainty is around:

- `available_minutes = 0` — the scheduler would return an empty schedule, but this is not explicitly tested.
- The `explain()` output format — verified visually in `main.py` but not asserted in any test.
- The Streamlit UI layer — no automated tests exist for what the user actually sees.

---

## 5. Reflection

**a. What went well**

The most satisfying part is the separation between the domain layer (`pawpal_system.py`) and the UI (`app.py`). Because all logic lives in plain Python classes with no Streamlit imports, every feature could be developed and tested in the terminal before touching the UI. The 14 tests run in under a second with no browser involved. That separation also meant the `ConflictDetector` could be added as a standalone class without modifying `Scheduler` at all — each class has one job and the boundaries held throughout the build.

**b. What you would improve**

Two things:

1. **Persistent storage** — right now, session state resets on every page refresh. Replacing the in-memory lists with a simple JSON file or SQLite database would make the app usable across sessions, which is the most important missing feature for a real pet owner.

2. **Multi-pet UI** — the conflict detection backend handles multiple pets, but the UI only schedules one at a time. Adding a second pet slot and running `ConflictDetector` across both schedules before displaying results would make the conflict warnings actually visible to the user.

**c. Key takeaway**

The lead architect role is not about writing every line — it is about making decisions that the AI cannot make on its own: what the system should do, where the boundaries between classes belong, and which suggestions to reject. Claude Code could propose a weighted-score sorting algorithm, implement `mark_complete()`, and write docstrings faster than any human. But it could not decide that medication tasks should never be bumped by shorter medium-priority tasks, or that a test failing because of a design change is a signal to fix the design rather than the test. Those judgments required understanding the problem, not just the code. The most important skill developed in this project was knowing when to accept a suggestion immediately, when to modify it, and when to push back entirely — and being able to explain why in each case.
