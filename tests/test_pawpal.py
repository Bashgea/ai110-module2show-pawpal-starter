from datetime import datetime, timedelta

import pytest

from pawpal_system import ConflictDetector, Owner, Pet, Schedule, Scheduler, Task


# ---------------------------------------------------------------------------
# Phase 2 tests (existing)
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    task = Task(title="Feed", duration_minutes=10, priority="high")
    assert task.status == "pending"
    task.mark_complete()
    assert task.status == "complete"


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task(title="Walk", duration_minutes=20, priority="high"))
    assert len(pet.tasks) == 1


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_owner(minutes=120):
    return Owner(name="Jordan", available_minutes=minutes, preferred_start_time="08:00")


def make_pet(species="other"):
    """Use species='other' to get minimal defaults and keep tests predictable."""
    return Pet(name="Buddy", species=species)


# ---------------------------------------------------------------------------
# 1. Sorting correctness
# ---------------------------------------------------------------------------

def test_schedule_entries_in_chronological_order():
    """Tasks added out of order by priority should appear chronologically after build."""
    owner = make_owner(120)
    pet = make_pet()
    tasks = [
        Task(title="Low task",    duration_minutes=10, priority="low"),
        Task(title="High task",   duration_minutes=10, priority="high"),
        Task(title="Medium task", duration_minutes=10, priority="medium"),
    ]
    schedule = Scheduler(owner=owner, pet=pet, tasks=tasks).build()
    schedule.sort_by_time()

    start_times = [e.start_time for e in schedule.entries]
    assert start_times == sorted(start_times), "Entries are not in chronological order"


def test_high_priority_scheduled_before_low():
    """A high-priority task must appear earlier in the schedule than a low-priority one."""
    owner = make_owner(120)
    pet = make_pet()
    tasks = [
        Task(title="Low task",  duration_minutes=10, priority="low"),
        Task(title="High task", duration_minutes=10, priority="high"),
    ]
    schedule = Scheduler(owner=owner, pet=pet, tasks=tasks).build()
    titles = [e.task.title for e in schedule.entries]

    assert titles.index("High task") < titles.index("Low task")


def test_same_priority_shorter_task_first():
    """Within the same priority, the shorter task should be scheduled first (SJF)."""
    owner = make_owner(120)
    pet = make_pet()
    tasks = [
        Task(title="Long high",  duration_minutes=30, priority="high"),
        Task(title="Short high", duration_minutes=5,  priority="high"),
    ]
    schedule = Scheduler(owner=owner, pet=pet, tasks=tasks).build()
    titles = [e.task.title for e in schedule.entries]

    assert titles.index("Short high") < titles.index("Long high")


# ---------------------------------------------------------------------------
# 2. Recurrence logic
# ---------------------------------------------------------------------------

def test_daily_task_stays_pending_after_complete():
    """mark_complete() on a daily task must keep status as 'pending'."""
    task = Task(title="Meds", duration_minutes=5, priority="high", frequency="daily")
    task.mark_complete()
    assert task.status == "pending"


def test_daily_task_advances_next_due_by_one_day():
    """mark_complete() on a daily task must set next_due to tomorrow."""
    task = Task(title="Meds", duration_minutes=5, priority="high", frequency="daily")
    task.mark_complete()
    expected = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    assert task.next_due == expected


def test_weekly_task_advances_next_due_by_seven_days():
    """mark_complete() on a weekly task must set next_due to today + 7 days."""
    task = Task(title="Grooming", duration_minutes=15, priority="medium", frequency="weekly")
    task.mark_complete()
    expected = (datetime.today() + timedelta(weeks=1)).strftime("%Y-%m-%d")
    assert task.next_due == expected


def test_non_recurring_task_becomes_complete():
    """mark_complete() on a plain task must set status to 'complete' (regression guard)."""
    task = Task(title="One-off", duration_minutes=10, priority="low")
    task.mark_complete()
    assert task.status == "complete"
    assert task.next_due == ""


def test_recurring_task_appears_in_schedule():
    """A task added via add_recurring_task() must appear in the built schedule."""
    owner = make_owner(120)
    pet = make_pet()
    pet.add_recurring_task(
        Task(title="Daily meds", duration_minutes=5, priority="high", frequency="daily")
    )
    schedule = Scheduler(owner=owner, pet=pet, tasks=[]).build()
    titles = [e.task.title for e in schedule.entries]
    assert "Daily meds" in titles


# ---------------------------------------------------------------------------
# 3. Conflict detection
# ---------------------------------------------------------------------------

def test_budget_conflict_detected_when_over():
    """ConflictDetector.check() must warn when combined schedules exceed owner budget."""
    owner = make_owner(30)  # tight budget
    pet_a = make_pet()
    pet_b = Pet(name="Luna", species="other")

    tasks_a = [Task(title="Task A", duration_minutes=20, priority="high")]
    tasks_b = [Task(title="Task B", duration_minutes=20, priority="high")]

    s_a = Scheduler(owner=owner, pet=pet_a, tasks=tasks_a).build()
    s_b = Scheduler(owner=owner, pet=pet_b, tasks=tasks_b).build()

    warnings = ConflictDetector().check(owner, [s_a, s_b])
    assert len(warnings) > 0
    assert "over budget" in warnings[0]


def test_no_budget_conflict_when_within_limit():
    """ConflictDetector.check() must return an empty list when schedules fit."""
    owner = make_owner(120)
    pet_a = make_pet()
    pet_b = Pet(name="Luna", species="other")

    tasks_a = [Task(title="Task A", duration_minutes=10, priority="high")]
    tasks_b = [Task(title="Task B", duration_minutes=10, priority="high")]

    s_a = Scheduler(owner=owner, pet=pet_a, tasks=tasks_a).build()
    s_b = Scheduler(owner=owner, pet=pet_b, tasks=tasks_b).build()

    assert ConflictDetector().check(owner, [s_a, s_b]) == []


def test_overlap_detected_when_pets_share_start_time():
    """detect_overlaps() must flag tasks that share the same time window."""
    owner = make_owner(120)
    pet_a = make_pet()
    pet_b = Pet(name="Luna", species="other")

    # Both pets get the same task pool and same start time → guaranteed overlap.
    shared_tasks = [Task(title="Feeding", duration_minutes=10, priority="high")]

    s_a = Scheduler(owner=owner, pet=pet_a, tasks=shared_tasks).build()
    s_b = Scheduler(owner=owner, pet=pet_b, tasks=shared_tasks).build()

    warnings = ConflictDetector().detect_overlaps([s_a, s_b])
    assert len(warnings) > 0
    assert "overlaps with" in warnings[0]


def test_no_overlap_for_single_pet_schedule():
    """detect_overlaps() on a single pet's schedule must return no warnings."""
    owner = make_owner(120)
    pet = make_pet()
    tasks = [Task(title="Walk", duration_minutes=20, priority="high")]
    schedule = Scheduler(owner=owner, pet=pet, tasks=tasks).build()

    assert ConflictDetector().detect_overlaps([schedule]) == []
