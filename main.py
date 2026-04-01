from pawpal_system import Owner, Pet, Task, Scheduler

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
# Custom tasks (on top of each pet's species defaults)
# ---------------------------------------------------------------------------

mochi_tasks = [
    Task(title="Grooming",        duration_minutes=15, priority="medium",
         description="Brush coat and check ears."),
    Task(title="Training session", duration_minutes=20, priority="low",
         description="Practice sit, stay, and recall."),
    Task(title="Vet medication",  duration_minutes=5,  priority="high",
         description="Administer daily allergy tablet."),
]

luna_tasks = [
    Task(title="Playtime",        duration_minutes=15, priority="medium",
         description="Interactive wand toy session."),
    Task(title="Nail trim",       duration_minutes=10, priority="low",
         description="Trim front claws."),
    Task(title="Vet medication",  duration_minutes=5,  priority="high",
         description="Administer daily thyroid tablet."),
]

# ---------------------------------------------------------------------------
# Build and print schedules
# ---------------------------------------------------------------------------

print("=" * 55)
print("              TODAY'S SCHEDULE")
print("=" * 55)

for pet, tasks in [(mochi, mochi_tasks), (luna, luna_tasks)]:
    schedule = Scheduler(owner=owner, pet=pet, tasks=tasks).build()
    print()
    print(schedule.explain())
    print("-" * 55)
