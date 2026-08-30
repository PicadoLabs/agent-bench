import pytest
from task_queue import TaskQueue


def test_task_submission_and_assignment():
    q = TaskQueue(heartbeat_timeout_seconds=5.0, max_retries=2)
    q.submit_task("t1", {"action": "send_email"})
    
    t = q.assign_next("worker-A", current_time=100.0)
    assert t is not None
    assert t.task_id == "t1"
    assert t.status == "RUNNING"
    assert t.assigned_worker == "worker-A"
    assert t.last_heartbeat == 100.0


def test_heartbeat_keeps_task_alive():
    q = TaskQueue(heartbeat_timeout_seconds=5.0, max_retries=2)
    q.submit_task("t1", {})
    q.assign_next("worker-A", current_time=100.0)

    # Worker sends heartbeat at t=104.0
    assert q.heartbeat("t1", current_time=104.0) is True

    # At t=106.0, only 2 seconds elapsed since last heartbeat (104.0)
    affected = q.check_dead_workers_and_requeue(current_time=106.0)
    assert len(affected) == 0
    assert q.tasks["t1"].status == "RUNNING"


def test_dead_worker_requeue_and_max_retries():
    q = TaskQueue(heartbeat_timeout_seconds=5.0, max_retries=1)
    q.submit_task("t1", {})
    q.assign_next("worker-A", current_time=100.0)

    # At t=106.0, worker-A missed heartbeat (> 5s)
    affected = q.check_dead_workers_and_requeue(current_time=106.0)
    assert affected == ["t1"]
    assert q.tasks["t1"].status == "PENDING"
    assert q.tasks["t1"].retry_count == 1
    assert q.tasks["t1"].assigned_worker is None

    # Re-assign to worker-B
    q.assign_next("worker-B", current_time=110.0)
    # worker-B also dies (> 5s later at t=116.0)
    affected2 = q.check_dead_workers_and_requeue(current_time=116.0)
    assert affected2 == ["t1"]
    # Should now be marked FAILED since retry_count reached max_retries (1)
    assert q.tasks["t1"].status == "FAILED"
