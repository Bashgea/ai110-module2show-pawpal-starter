from pawpal_system import Task, Pet


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
