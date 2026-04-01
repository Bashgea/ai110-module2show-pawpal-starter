import streamlit as st
from pawpal_system import ConflictDetector, Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.divider()

# ---------------------------------------------------------------------------
# Owner + Pet setup
# ---------------------------------------------------------------------------

st.subheader("Owner & Pet")

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
    available_minutes = st.number_input(
        "Available minutes today", min_value=10, max_value=480, value=60
    )
with col2:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])

# Persist Owner and Pet in session_state so they survive reruns
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name, available_minutes=int(available_minutes))
if "pet" not in st.session_state:
    st.session_state.pet = Pet(name=pet_name, species=species)

st.divider()

# ---------------------------------------------------------------------------
# Add tasks
# ---------------------------------------------------------------------------

st.subheader("Add a Task")

col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    frequency = st.selectbox("Repeats", ["once", "daily", "weekly"])

if st.button("Add task"):
    new_task = Task(
        title=task_title,
        duration_minutes=int(duration),
        priority=priority,
        frequency="" if frequency == "once" else frequency,
    )
    if frequency == "once":
        st.session_state.pet.add_task(new_task)
    else:
        st.session_state.pet.add_recurring_task(new_task)
    st.success(f"Added: {task_title} ({priority} priority, {frequency})")

# Display current task list
one_off = st.session_state.pet.tasks
recurring = st.session_state.pet.recurring_tasks

if one_off:
    st.markdown("**One-off tasks**")
    st.table([
        {"title": t.title, "duration (min)": t.duration_minutes,
         "priority": t.priority, "status": t.status}
        for t in one_off
    ])

if recurring:
    st.markdown("**Recurring tasks**")
    st.table([
        {"title": t.title, "duration (min)": t.duration_minutes,
         "priority": t.priority, "repeats": t.frequency, "next due": t.next_due or "today"}
        for t in recurring
    ])

if not one_off and not recurring:
    st.info("No tasks yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Generate schedule
# ---------------------------------------------------------------------------

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    owner = st.session_state.owner
    pet = st.session_state.pet

    schedule = Scheduler(owner=owner, pet=pet, tasks=pet.tasks).build()
    schedule.sort_by_time()

    # ---- Budget meter ----
    used = schedule.total_duration
    budget = owner.available_minutes
    pct = min(used / budget, 1.0)
    st.markdown(f"**Time used:** {used} min of {budget} min available")
    st.progress(pct)

    if used > budget:
        st.warning(f"Over budget by {used - budget} min — some tasks were skipped.")
    elif used == budget:
        st.success("Perfect fit — full budget used.")
    else:
        st.success(f"Schedule fits with {budget - used} min to spare.")

    # ---- Conflict warnings ----
    detector = ConflictDetector()
    budget_warnings = detector.check(owner, [schedule])
    overlap_warnings = detector.detect_overlaps([schedule])

    for w in budget_warnings + overlap_warnings:
        st.warning(f"⚠️ {w}")

    # ---- Schedule table ----
    if schedule.entries:
        st.markdown("#### Today's plan")
        st.table([
            {
                "time": f"{e.start_time} – {e.end_time}",
                "task": e.task.title,
                "priority": e.task.priority,
                "duration (min)": e.task.duration_minutes,
                "status": e.task.status,
            }
            for e in schedule.entries
        ])
    else:
        st.warning("No tasks could be scheduled. Try adding tasks or increasing available time.")

    # ---- Pending vs complete breakdown ----
    pending = schedule.filter_by_status("pending")
    complete = schedule.filter_by_status("complete")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Pending tasks", len(pending))
    with col2:
        st.metric("Completed tasks", len(complete))
