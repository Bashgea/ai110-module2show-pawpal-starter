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

    def priority_rank(self) -> int:
        """Return a numeric rank so tasks can be sorted (higher = more urgent)."""
        return {"low": 1, "medium": 2, "high": 3}.get(self.priority, 0)


@dataclass
class Pet:
    name: str
    species: str           # "dog" | "cat" | "other"
    age: int = 0
    special_needs: list[str] = field(default_factory=list)

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
                lines.append(f"    → {entry.reason}")

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

        # Merge caller-supplied tasks with pet species defaults.
        # Deduplicate by title so the same task isn't scheduled twice.
        seen_titles: set[str] = set()
        all_tasks: list[Task] = []
        for task in self.tasks + (self.pet.get_default_tasks() or []):
            if task.title not in seen_titles:
                seen_titles.add(task.title)
                all_tasks.append(task)

        # Sort by priority descending; use title as tie-breaker for stable ordering.
        sorted_tasks = sorted(all_tasks, key=lambda t: (-t.priority_rank(), t.title))

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
