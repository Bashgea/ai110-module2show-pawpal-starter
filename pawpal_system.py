from dataclasses import dataclass, field
from datetime import datetime, timedelta


# ---------------------------------------------------------------------------
# Data classes (pure data, no scheduling logic)
# ---------------------------------------------------------------------------

@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str          # "low" | "medium" | "high"
    description: str = ""
    status: str = "pending"     # "pending" | "complete"
    recurring: bool = False     # True = include in every scheduled run
    frequency: str = ""         # "" | "daily" | "weekly"
    next_due: str = ""          # "YYYY-MM-DD"; set automatically on completion

    def mark_complete(self) -> None:
        """Mark this task as complete.

        For recurring tasks (frequency="daily" or "weekly"), automatically
        resets status to "pending" and advances next_due by the appropriate
        timedelta so the task reappears in the next scheduled run.
        """
        self.status = "complete"
        if self.frequency == "daily":
            self.status = "pending"
            self.next_due = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        elif self.frequency == "weekly":
            self.status = "pending"
            self.next_due = (datetime.today() + timedelta(weeks=1)).strftime("%Y-%m-%d")

    def priority_rank(self) -> int:
        """Return a numeric rank so tasks can be sorted (higher = more urgent)."""
        return {"low": 1, "medium": 2, "high": 3}.get(self.priority, 0)


@dataclass
class Pet:
    name: str
    species: str           # "dog" | "cat" | "other"
    age: int = 0
    special_needs: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)
    recurring_tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a one-off task to this pet's task list."""
        self.tasks.append(task)

    def add_recurring_task(self, task: Task) -> None:
        """Add a daily recurring task (included in every scheduled run)."""
        task.recurring = True
        self.recurring_tasks.append(task)

    def get_default_tasks(self) -> list[Task]:
        """Return a species-appropriate list of default tasks."""
        if self.species == "dog":
            return [
                Task(title="Morning walk", duration_minutes=20, priority="high",
                     description="Daily walk for exercise and bathroom needs."),
                Task(title="Feeding", duration_minutes=10, priority="high",
                     description="Morning meal."),
                Task(title="Fresh water", duration_minutes=5, priority="medium",
                     description="Refill water bowl."),
            ]
        if self.species == "cat":
            return [
                Task(title="Feeding", duration_minutes=10, priority="high",
                     description="Morning meal."),
                Task(title="Fresh water", duration_minutes=5, priority="medium",
                     description="Refill water bowl."),
                Task(title="Litter box", duration_minutes=10, priority="high",
                     description="Clean litter box."),
            ]
        # "other" — minimal safe defaults
        return [
            Task(title="Feeding", duration_minutes=10, priority="high",
                 description="Morning meal."),
            Task(title="Fresh water", duration_minutes=5, priority="medium",
                 description="Refill water bowl."),
        ]


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferred_start_time: str = "08:00"  # 24-hour HH:MM, set by the owner


# ---------------------------------------------------------------------------
# Schedule building blocks
# ---------------------------------------------------------------------------

@dataclass
class ScheduledEntry:
    task: Task
    start_time: str        # e.g. "08:00"
    end_time: str          # e.g. "08:20"
    reason: str = ""


class Schedule:
    def __init__(self, owner: Owner, pet: Pet):
        self.owner = owner
        self.pet = pet
        self.entries: list[ScheduledEntry] = []
        self.total_duration: int = 0

    def add_entry(self, entry: ScheduledEntry) -> None:
        """Append a ScheduledEntry and update total_duration."""
        self.entries.append(entry)
        self.total_duration += entry.task.duration_minutes

    def sort_by_time(self) -> None:
        """Sort schedule entries in place by their start time, earliest first.

        Uses the HH:MM start_time string stored on each ScheduledEntry as the
        sort key, parsing it into a datetime so the comparison is numeric rather
        than lexicographic.  Mutates self.entries directly; returns nothing.

        Example:
            schedule.sort_by_time()
            # entries are now ordered 08:00 → 08:05 → 08:15 → ...
        """
        self.entries.sort(key=lambda e: datetime.strptime(e.start_time, "%H:%M"))

    def filter_by_status(self, status: str) -> list[ScheduledEntry]:
        """Return a filtered list of entries whose task has the given status.

        Args:
            status: Either "pending" (task not yet done) or "complete"
                    (task already marked done via Task.mark_complete()).

        Returns:
            A new list containing only the ScheduledEntry objects whose
            task.status matches the requested value.  The original
            self.entries list is not modified.

        Example:
            pending = schedule.filter_by_status("pending")
        """
        return [e for e in self.entries if e.task.status == status]

    def is_feasible(self) -> bool:
        """Return True if total_duration fits within owner's available_minutes."""
        return self.total_duration <= self.owner.available_minutes

    def explain(self) -> str:
        """Return a human-readable summary of the schedule with per-entry reasoning."""
        if not self.entries:
            return f"No tasks could be scheduled for {self.pet.name} today."

        lines = [
            f"Daily plan for {self.pet.name} ({self.owner.name})",
            f"Total time: {self.total_duration} min / {self.owner.available_minutes} min available",
            "",
        ]
        for entry in self.entries:
            lines.append(
                f"  {entry.start_time} – {entry.end_time}  {entry.task.title}"
                f"  [{entry.task.priority} priority]"
            )
            if entry.reason:
                lines.append(f"    -> {entry.reason}")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Scheduling engine
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, owner: Owner, pet: Pet, tasks: list[Task]):
        self.owner = owner
        self.pet = pet
        self.tasks = tasks

    def build(self) -> Schedule:
        """Merge pet defaults into task list, sort by priority, fit tasks into
        the owner's available time window, and return a Schedule."""

        # Merge caller-supplied tasks, pet recurring tasks, and species defaults.
        # Deduplicate by title so the same task isn't scheduled twice.
        seen_titles: set[str] = set()
        all_tasks: list[Task] = []
        candidate_pool = self.tasks + self.pet.recurring_tasks + (self.pet.get_default_tasks() or [])
        for task in candidate_pool:
            if task.title not in seen_titles:
                seen_titles.add(task.title)
                all_tasks.append(task)

        # Filter out already-completed tasks.
        all_tasks = [t for t in all_tasks if t.status != "complete"]

        # Sort: priority descending, then duration ascending (Algorithm A — SJF tie-break).
        sorted_tasks = sorted(all_tasks, key=lambda t: (-t.priority_rank(), t.duration_minutes))

        schedule = Schedule(self.owner, self.pet)
        current_time = datetime.strptime(self.owner.preferred_start_time, "%H:%M")
        remaining_minutes = self.owner.available_minutes

        for task in sorted_tasks:
            # Check budget before adding — never produce an over-budget schedule.
            if task.duration_minutes > remaining_minutes:
                continue

            start_str = current_time.strftime("%H:%M")
            end_dt = current_time + timedelta(minutes=task.duration_minutes)
            end_str = end_dt.strftime("%H:%M")

            reason = (
                f"Scheduled at {start_str} because priority is '{task.priority}'. "
                f"Duration: {task.duration_minutes} min."
            )
            schedule.add_entry(
                ScheduledEntry(task=task, start_time=start_str, end_time=end_str, reason=reason)
            )

            current_time = end_dt
            remaining_minutes -= task.duration_minutes

        return schedule


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

class ConflictDetector:
    def check(self, owner: Owner, schedules: list[Schedule]) -> list[str]:
        """Return a list of warning strings if the combined schedules exceed
        the owner's available minutes. Empty list means no conflicts."""
        warnings: list[str] = []
        total = sum(s.total_duration for s in schedules)
        if total > owner.available_minutes:
            over = total - owner.available_minutes
            pet_names = ", ".join(s.pet.name for s in schedules)
            warnings.append(
                f"Combined schedule for {pet_names} is {total} min, "
                f"but {owner.name} only has {owner.available_minutes} min available "
                f"({over} min over budget)."
            )
        return warnings

    def detect_overlaps(self, schedules: list[Schedule]) -> list[str]:
        """Detect time-window overlaps across all entries in the given schedules.

        Flattens every ScheduledEntry from every Schedule into a single list,
        then checks each unique pair using the standard interval-overlap
        condition: two intervals [s_a, e_a) and [s_b, e_b) overlap when
        s_a < e_b AND s_b < e_a.

        Args:
            schedules: One or more Schedule objects to check together.
                       Typically one schedule per pet sharing the same owner.

        Returns:
            A list of human-readable warning strings, one per conflicting pair.
            Returns an empty list when no overlaps are found.

        Example:
            warnings = detector.detect_overlaps([mochi_schedule, luna_schedule])
            for w in warnings:
                print(w)
        """
        warnings: list[str] = []

        # Flatten all entries, tagging each with its pet name.
        all_entries: list[tuple[str, ScheduledEntry]] = [
            (s.pet.name, e) for s in schedules for e in s.entries
        ]

        for i in range(len(all_entries)):
            pet_a, entry_a = all_entries[i]
            start_a = datetime.strptime(entry_a.start_time, "%H:%M")
            end_a   = datetime.strptime(entry_a.end_time,   "%H:%M")

            for j in range(i + 1, len(all_entries)):
                pet_b, entry_b = all_entries[j]
                start_b = datetime.strptime(entry_b.start_time, "%H:%M")
                end_b   = datetime.strptime(entry_b.end_time,   "%H:%M")

                # Overlap when one interval starts before the other ends.
                if start_a < end_b and start_b < end_a:
                    warnings.append(
                        f"WARNING: '{entry_a.task.title}' ({pet_a}, "
                        f"{entry_a.start_time}–{entry_a.end_time}) overlaps with "
                        f"'{entry_b.task.title}' ({pet_b}, "
                        f"{entry_b.start_time}–{entry_b.end_time})."
                    )
        return warnings
