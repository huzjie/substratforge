# -*- coding: utf-8 -*-
"""任务队列：向沙箱投递异步任务，跟踪执行状态与结果。

任务模型：
    Task(id, sandbox_id, action, payload, status, created_at, ...)

动作（action）对应沙箱可执行的原语：
    spawn / suspend / resume / destroy / exec / snapshot / stats

队列为内存实现（可插拔，生产可换 Redis/AMQP，见 docs/runtime-task.md）。
"""
from __future__ import annotations

import queue
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass
class Task:
    """一个待执行 / 已执行的任务。"""
    action: str
    payload: dict[str, Any] = field(default_factory=dict)
    sandbox_id: str = ""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    status: TaskStatus = TaskStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    result: Any = None
    error: str = ""

    def as_dict(self) -> dict:
        return {
            "id": self.id, "action": self.action, "sandbox_id": self.sandbox_id,
            "status": self.status.value, "payload": self.payload,
            "created_at": self.created_at, "finished_at": self.finished_at,
            "result": self.result, "error": self.error,
        }


class TaskQueue:
    """线程安全任务队列 + 工作线程池。"""

    def __init__(self, workers: int = 4):
        self._q: queue.Queue[Task] = queue.Queue()
        self._results: dict[str, Task] = {}
        self._lock = threading.Lock()
        self._workers = workers
        self._threads: list[threading.Thread] = []
        self._handlers: dict[str, Callable[[Task], Any]] = {}

    def register_handler(self, action: str, fn: Callable[[Task], Any]) -> None:
        """注册动作处理器。"""
        self._handlers[action] = fn

    def submit(self, action: str, payload: dict | None = None, sandbox_id: str = "") -> Task:
        task = Task(action=action, payload=payload or {}, sandbox_id=sandbox_id)
        with self._lock:
            self._results[task.id] = task
        self._q.put(task)
        return task

    def get(self, task_id: str) -> Optional[Task]:
        with self._lock:
            return self._results.get(task_id)

    def start(self) -> None:
        """启动工作线程。"""
        for _ in range(self._workers):
            t = threading.Thread(target=self._worker, daemon=True)
            t.start()
            self._threads.append(t)

    def _worker(self) -> None:
        while True:
            task = self._q.get()
            task.status = TaskStatus.RUNNING
            task.started_at = time.time()
            try:
                handler = self._handlers.get(task.action)
                if handler is None:
                    raise KeyError(f"未注册的动作: {task.action}")
                task.result = handler(task)
                task.status = TaskStatus.SUCCEEDED
            except Exception as exc:  # noqa: BLE001
                task.error = str(exc)
                task.status = TaskStatus.FAILED
            finally:
                task.finished_at = time.time()
                self._q.task_done()

    def pending_count(self) -> int:
        return self._q.qsize()


__all__ = ["TaskQueue", "Task", "TaskStatus"]
