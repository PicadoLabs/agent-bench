# task_queue.py - Asynchronous Job Queue & Dead Worker Recovery
from typing import Dict, Any, List, Optional
import time


class Task:
    def __init__(self, task_id: str, payload: Dict[str, Any]):
        self.task_id = task_id
        self.payload = payload
        self.status = "PENDING"  # PENDING, RUNNING, COMPLETED, FAILED
        self.assigned_worker: Optional[str] = None
        self.last_heartbeat: Optional[float] = None
        self.retry_count = 0


class TaskQueue:
    def __init__(self, heartbeat_timeout_seconds: float = 5.0, max_retries: int = 2):
        self.heartbeat_timeout = heartbeat_timeout_seconds
        self.max_retries = max_retries
        self.tasks: Dict[str, Task] = {}

    def submit_task(self, task_id: str, payload: Dict[str, Any]) -> Task:
        task = Task(task_id, payload)
        self.tasks[task_id] = task
        return task

    def assign_next(self, worker_id: str, current_time: float) -> Optional[Task]:
        for task in self.tasks.values():
            if task.status == "PENDING":
                task.status = "RUNNING"
                task.assigned_worker = worker_id
                task.last_heartbeat = current_time
                return task
        return None

    def heartbeat(self, task_id: str, current_time: float) -> bool:
        task = self.tasks.get(task_id)
        if task and task.status == "RUNNING":
            task.last_heartbeat = current_time
            return True
        return False

    def check_dead_workers_and_requeue(self, current_time: float) -> List[str]:
        """
        Scan running tasks:
        - If (current_time - last_heartbeat) > heartbeat_timeout:
          - If task.retry_count < max_retries:
            - Increment retry_count, set status="PENDING", clear assigned_worker.
          - Else:
            - Set status="FAILED" (exceeded max retries).
        Return list of recovered or failed task IDs.
        """
        affected = []
        for task in self.tasks.values():
            if task.status == "RUNNING":
                # BUG: Off-by-one / inverted comparison
                elapsed = current_time - (task.last_heartbeat or 0.0)
                if elapsed < self.heartbeat_timeout:  # BUG: < instead of >
                    task.retry_count += 1
                    task.status = "PENDING"
                    affected.append(task.task_id)
        return affected
