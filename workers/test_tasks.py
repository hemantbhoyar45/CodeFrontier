from workers.tasks import add


def test_sample_add_task_runs_without_a_worker_broker() -> None:
    assert add.run(2, 3) == 5
