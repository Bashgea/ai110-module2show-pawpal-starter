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
        pass


@dataclass
class Pet:
    name: str
    species: str           # "dog" | "cat" | "other"
    age: int = 0
    special_needs: list[str] = field(default_factory=list)

    def get_default_tasks(self) -> list[Task]:
        """Return a species-appropriate list of default tasks."""
        pass


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
        pass

    def is_feasible(self) -> bool:
        """Return True if total_duration fits within owner's available_minutes."""
        pass

    def explain(self) -> str:
        """Return a human-readable summary of the schedule with per-entry reasoning."""
        pass


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
        pass
