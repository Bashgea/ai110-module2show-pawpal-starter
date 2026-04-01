# PawPal+ UML Class Diagram

```mermaid
classDiagram
    class Task {
        +String title
        +int duration_minutes
        +String priority
        +String description
        +String status
        +bool recurring
        +String frequency
        +String next_due
        +priority_rank() int
        +mark_complete() None
    }

    class ScheduledEntry {
        +Task task
        +String start_time
        +String end_time
        +String reason
    }

    class Pet {
        +String name
        +String species
        +int age
        +List~String~ special_needs
        +List~Task~ tasks
        +List~Task~ recurring_tasks
        +add_task(task) None
        +add_recurring_task(task) None
        +get_default_tasks() List~Task~
    }

    class Owner {
        +String name
        +int available_minutes
        +String preferred_start_time
    }

    class Schedule {
        +Owner owner
        +Pet pet
        +List~ScheduledEntry~ entries
        +int total_duration
        +add_entry(entry) None
        +sort_by_time() None
        +filter_by_status(status) List~ScheduledEntry~
        +is_feasible() bool
        +explain() String
    }

    class Scheduler {
        +Owner owner
        +Pet pet
        +List~Task~ tasks
        +build() Schedule
    }

    class ConflictDetector {
        +check(owner, schedules) List~String~
        +detect_overlaps(schedules) List~String~
    }

    Owner "1" --> "1" Pet : cares for
    Owner "1" --> "1" Scheduler : uses
    Pet "1" --> "*" Task : one-off tasks
    Pet "1" --> "*" Task : recurring tasks
    Pet "1" --> "*" Task : species defaults
    Scheduler "1" --> "*" Task : prioritizes
    Scheduler "1" --> "1" Schedule : produces
    Schedule "1" --> "1" Owner : belongs to
    Schedule "1" --> "1" Pet : belongs to
    Schedule "1" --> "*" ScheduledEntry : contains
    ScheduledEntry "1" --> "1" Task : wraps
    ConflictDetector ..> Owner : reads budget
    ConflictDetector ..> Schedule : inspects entries
```

## What changed from Phase 1

**`Task`** — added `status`, `recurring`, `frequency`, and `next_due` fields to support
completion tracking and auto-recurrence. Added `mark_complete()` which advances `next_due`
via `timedelta` when `frequency` is set.

**`Pet`** — added two task lists (`tasks` for one-off, `recurring_tasks` for daily/weekly
habits) and the methods to populate them. The original diagram only showed species defaults.

**`Schedule`** — added `sort_by_time()` (sorts entries by HH:MM start time) and
`filter_by_status()` (returns a filtered subset of entries by task status).

**`ConflictDetector`** — new class, not in the original design. Provides two checks:
`check()` for budget overruns across multiple pets, and `detect_overlaps()` for
time-window collisions between any two scheduled entries.

**Relationships** — `Pet --> Task` is now three distinct arrows (one-off, recurring,
species defaults) instead of a single "has default" edge. `ConflictDetector` uses dashed
dependency arrows (`..>`) to `Owner` and `Schedule` since it reads them without owning them.
