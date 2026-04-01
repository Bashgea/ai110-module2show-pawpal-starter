# Smart Algorithm Decisions

Answers to the three open questions from the Phase 3 planning notes, with reasoning.

---

## 1. Sorting — Algorithm A vs B

**Verdict: Use Algorithm A.**

### How they differ on the real merged task list

`Scheduler.build()` merges caller-supplied tasks with `get_default_tasks()`, so the
pool for Mochi (dog) ends up with multiple high-priority tasks (Vet medication 5 min,
Feeding 10 min, Morning walk 20 min), medium tasks (Fresh water 5 min, Grooming 15 min),
and low tasks (Training session 20 min).

| Algorithm | Rule | Mochi high-block result |
|---|---|---|
| A | `priority_rank()` desc → `duration_minutes` asc | Meds (5) → Feeding (10) → Walk (20) — all highs together |
| B | `score = priority_rank() * 10 - duration_minutes` desc | Fresh water scores 15, Morning walk scores 10 → **Fresh water jumps into the high block** |

Algorithm B's single score can pull a medium task above a high task when the medium task
is short. That's hard to explain out loud as a pet-care plan ("we're doing fresh water
before the morning walk because the math said so").

Algorithm A keeps a strict **all-high → all-medium → all-low** ladder, with
shortest-first only as a tie-break *within* a priority level. That matches the natural
story: "finish every urgent thing first, then maintenance, then optional."

### Implementation (replace existing sort in `Scheduler.build()`)

```python
sorted_tasks = sorted(all_tasks, key=lambda t: (-t.priority_rank(), t.duration_minutes))
```

---

## 2. Recurring Tasks — UI or code-only?

**Decision: Code-only for the initial implementation.**

### Why

- The feature is a model change first: `recurring: bool` on `Task`,
  `recurring_tasks: list[Task]` on `Pet`, merge logic in `Scheduler.build()`.
  Proving it works in tests and a small demo script is enough to demonstrate the concept.
- Adding UI editing opens product questions that are out of scope right now:
  separate list vs checkbox, whether edits apply to "every day" or "just this run,"
  and how that interacts with deduplication against one-off tasks and species defaults.
- The README asks for task add/edit in general — not recurring as a first-class UI
  concept.

### When to add UI

Add a "Recurring" checkbox (or a second "Daily habits" table) in `app.py` once
`Scheduler` + tests behave correctly and you're ready to define how checkbox state
maps to `pet.recurring_tasks` vs `pet.tasks`.

---

## 3. Shared Time Budget — Equal split or first-come-first-served?

**Decision: Equal split as the default.**

### Comparison

| Approach | Pros | Cons |
|---|---|---|
| Equal split | Predictable; easy to explain; stable tests; fair to both pets | Ignores real imbalance (one pet may need more that day) |
| First-come-first-served | Full flexibility; mirrors natural planning flow | Order must be explicitly defined; second pet can be starved silently |

### Why equal split fits this project

- One clear rule: `per_pet_budget = owner.available_minutes // n_pets`; any remainder goes to the last pet (e.g. 121 minutes, 2 pets → 60 + 61).
- Demos are stable — Mochi and Luna always each get 60 minutes out of 120.
- Tests are straightforward: two pets × half budget → assert neither schedule
  silently exceeds its share.
- `ConflictDetector` still catches the case where even the halved budget isn't enough.

### When to switch

Use FCFS (or a hybrid) if you later build a single combined timeline or add explicit
pet-ordering in the UI, and are willing to surface "X minutes remaining" so the
second pet's plan stays interpretable.

---

## Summary

| Question | Decision |
|---|---|
| Sorting algorithm | **A** — priority ladder, SJF tie-break within priority |
| Recurring tasks UI | **Code-only** for now; UI checkbox deferred |
| Shared budget | **Equal split** (`available_minutes // n_pets`) |
