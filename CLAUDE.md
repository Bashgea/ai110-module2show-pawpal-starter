# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Activate virtual environment (Windows)
.venv\Scripts\activate

# Run the Streamlit app
streamlit run app.py

# Run tests
pytest

# Run a single test file
pytest tests/test_scheduler.py

# Run a single test
pytest tests/test_scheduler.py::test_function_name
```

## Architecture

**PawPal+** is a Streamlit-based pet care scheduling app. The stack is Python + Streamlit for UI, pytest for tests.

`app.py` is the single UI entry point — it is intentionally a thin starter. The core domain logic (classes, scheduling algorithm) needs to be implemented separately and imported into `app.py`.

### Intended design (from README)

The system should have:
- Domain classes: `Pet`, `Owner`, `Task`, `Schedule` (to be created)
- A scheduling algorithm that takes owner/pet info + a list of tasks with durations and priorities, and produces an ordered daily plan with reasoning
- Tests covering key scheduling behaviors (priority ordering, time constraints, edge cases)

### Suggested implementation flow

1. Design UML diagram
2. Create class stubs (no logic)
3. Implement scheduling logic incrementally
4. Add pytest tests for scheduling behavior
5. Connect classes to `app.py` — replace the `st.warning("Not implemented yet")` block in the "Generate schedule" button handler with actual scheduler calls
6. Display the schedule and per-task reasoning in the UI

### Key Streamlit patterns in `app.py`

- `st.session_state.tasks` holds the in-memory task list across reruns
- Tasks are dicts: `{"title": str, "duration_minutes": int, "priority": str}`
- The "Generate schedule" button at line 76 is the integration point for the scheduler
