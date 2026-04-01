from pawpal_system import Owner, Pet, Task, Scheduler, ConflictDetector

# ---------------------------------------------------------------------------
# Setup: one owner, two pets
# ---------------------------------------------------------------------------

owner = Owner(
    name="Jordan",
    available_minutes=120,
    preferred_start_time="08:00",
)

mochi = Pet(name="Mochi", species="dog", age=3)
luna  = Pet(name="Luna",  species="cat", age=5)

# ---------------------------------------------------------------------------
# Step 2 demo: tasks added out of order, then sorted by start time
# ---------------------------------------------------------------------------

mochi_tasks = [
    Task(title="Grooming",         duration_minutes=15, priority="medium",
         description="Brush coat and check ears."),
    Task(title="Training session", duration_minutes=20, priority="low",
         description="Practice sit, stay, and recall."),
    Task(title="Vet medication",   duration_minutes=5,  priority="high",
         description="Administer daily allergy tablet."),
]

luna_tasks = [
    Task(title="Playtime",         duration_minutes=15, priority="medium",
         description="Interactive wand toy session."),
    Task(title="Nail trim",        duration_minutes=10, priority="low",
         description="Trim front claws."),
    Task(title="Vet medication",   duration_minutes=5,  priority="high",
         description="Administer daily thyroid tablet."),
]

mochi_schedule = Scheduler(owner=owner, pet=mochi, tasks=mochi_tasks).build()
luna_schedule  = Scheduler(owner=owner, pet=luna,  tasks=luna_tasks).build()

print("=" * 55)
print("         STEP 2 — SORT BY TIME + FILTER BY STATUS")
print("=" * 55)

mochi_schedule.sort_by_time()
print("\nMochi's schedule sorted by start time:")
for e in mochi_schedule.entries:
    print(f"  {e.start_time} – {e.end_time}  {e.task.title}  [{e.task.status}]")

pending = mochi_schedule.filter_by_status("pending")
print(f"\nPending tasks only ({len(pending)} of {len(mochi_schedule.entries)}):")
for e in pending:
    print(f"  {e.task.title}")

# ---------------------------------------------------------------------------
# Step 3 demo: recurring task auto-advances on completion
# ---------------------------------------------------------------------------

print("\n" + "=" * 55)
print("         STEP 3 — RECURRING TASK AUTO-RECURRENCE")
print("=" * 55)

daily_med = Task(
    title="Vet medication",
    duration_minutes=5,
    priority="high",
    frequency="daily",
    description="Daily allergy tablet — recurs automatically.",
)
mochi.add_recurring_task(daily_med)

print(f"\nBefore mark_complete(): status='{daily_med.status}', next_due='{daily_med.next_due}'")
daily_med.mark_complete()
print(f"After  mark_complete(): status='{daily_med.status}', next_due='{daily_med.next_due}'")
print("(Status reset to 'pending' and next_due advanced by 1 day — task will reappear tomorrow.)")

# ---------------------------------------------------------------------------
# Step 4 demo: overlap conflict detection
# ---------------------------------------------------------------------------

print("\n" + "=" * 55)
print("         STEP 4 — TIME OVERLAP CONFLICT DETECTION")
print("=" * 55)

# Force an overlap: give both pets the same start time so their schedules clash.
overlap_owner = Owner(name="Jordan", available_minutes=120, preferred_start_time="08:00")
s1 = Scheduler(owner=overlap_owner, pet=mochi, tasks=mochi_tasks).build()
s2 = Scheduler(owner=overlap_owner, pet=luna,  tasks=luna_tasks).build()

detector = ConflictDetector()

budget_warnings = detector.check(overlap_owner, [s1, s2])
overlap_warnings = detector.detect_overlaps([s1, s2])

print("\nBudget conflicts:")
for w in budget_warnings:
    print(f"  {w}")
if not budget_warnings:
    print("  None")

print("\nTime overlap conflicts:")
for w in overlap_warnings:
    print(f"  {w}")
if not overlap_warnings:
    print("  None")

# ---------------------------------------------------------------------------
# Full schedules
# ---------------------------------------------------------------------------

print("\n" + "=" * 55)
print("              TODAY'S FULL SCHEDULE")
print("=" * 55)

for schedule in [mochi_schedule, luna_schedule]:
    print()
    print(schedule.explain())
    print("-" * 55)
