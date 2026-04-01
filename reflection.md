# PawPal+ Project Reflection

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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
