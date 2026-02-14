from __future__ import annotations

from threading import Lock

from artiisly_automation.core.models import TaskRecord


class InMemoryTaskRepository:
    def __init__(self) -> None:
        self._data: dict[str, TaskRecord] = {}
        self._lock = Lock()

    def save(self, task: TaskRecord) -> None:
        with self._lock:
            self._data[task.workflow_id] = task

    def get(self, workflow_id: str) -> TaskRecord | None:
        with self._lock:
            return self._data.get(workflow_id)
