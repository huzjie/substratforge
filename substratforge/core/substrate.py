# -*- coding: utf-8 -*-
"""Substrate 主引擎：把沙箱 / 快照 / 调度 / 存储 / 运行时串成一条流水线。

这是整个库的编排中枢，对外暴露：

- spawn(name, ...)          创建沙箱（热态）
- suspend(name, tags)       挂起 -> 快照落盘 -> 释放运行环境（冷态）
- resume(name, snapshot_id) 从快照恢复（受 resume 预算约束）
- destroy(name)             销毁
- list_sandboxes() / list_snapshots() / get()
- tick()                    调度心跳：自动挂起空闲沙箱、超限驱逐
- demo()                    零依赖挂起/恢复演示
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Optional

from ..config import Config, load_config
from ..errors import (
    AlreadyExistsError, NotFoundError, SandboxError, SchedulerError,
)
from ..security.audit import AuditLog
from ..types import (
    IsolationLevel, ResourceQuota, SandboxRuntimeInfo, SandboxSpec,
    SandboxState, SnapshotInfo, SchedulerStats, new_id,
)
from ..utils import ensure_dir, monotonic_ms
from .registry import Registry

# 惰性导入子包，避免模块加载顺序问题
def _imports():
    from ..sandbox import get_backend  # noqa: F401
    from ..snapshot import SnapshotEngine  # noqa: F401
    from ..scheduler import DensityScheduler  # noqa: F401
    from ..storage import LocalStore, MemoryStore  # noqa: F401
    from ..runtime import HeartbeatWatchdog, Lifecycle  # noqa: F401


class Substrate:
    """高密度智能体基板主引擎。"""

    def __init__(self, config: Config | None = None):
        self.config = config or Config()
        _imports()

        self._root = ensure_dir(
            Path(self.config.get("sandbox.root_dir", "~/.substratforge/sandboxes")).expanduser()
        )

        # 沙箱后端（按默认隔离等级）
        default_iso = self.config.get("sandbox.default_isolation", "process")
        self.backend = self._make_backend(default_iso)

        # 存储后端
        from ..storage import LocalStore, MemoryStore
        storage_cfg = self.config.section("storage")
        backend_name = storage_cfg.get("backend", "local")
        if backend_name == "memory":
            self.store = MemoryStore()
        else:
            root = Path(storage_cfg.get("root", "~/.substratforge/store")).expanduser()
            self.store = LocalStore(root)

        # 快照引擎
        from ..snapshot import SnapshotEngine
        snap_cfg = self.config.section("snapshot")
        self.snapshot = SnapshotEngine(
            snapshot_dir=Path(snap_cfg.get("dir", "~/.substratforge/snapshots")).expanduser(),
            storage=self.store,
            format=snap_cfg.get("format", "tar"),
            compression=snap_cfg.get("compression", "zstd"),
            delta=snap_cfg.get("delta", True),
        )

        # 调度器
        from ..scheduler import DensityScheduler
        sched_cfg = self.config.section("scheduler")
        self.scheduler = DensityScheduler(
            eviction_policy=sched_cfg.get("eviction_policy", "lru"),
            max_suspended=sched_cfg.get("max_suspended_per_host", 1000),
            max_running=sched_cfg.get("max_running_per_host", 64),
            idle_suspend_after=sched_cfg.get("idle_suspend_after", 300),
            resume_budget_ms=sched_cfg.get("resume_budget_ms", 500),
        )

        # 心跳看门狗
        from ..runtime import HeartbeatWatchdog
        self.watchdog = HeartbeatWatchdog(
            idle_timeout=self.config.get("sandbox.max_idle_seconds", 300)
        )

        # 安全策略 + 审计
        from ..security.policy import SecurityPolicy
        sec = self.config.section("security")
        self.policy = SecurityPolicy(
            min_isolation=sec.get("min_isolation", "process"),
            default_quota=ResourceQuota(**(sec.get("default_quota", {}))),
        )

        audit_path = Path(self.config.get("storage.root", "~/.substratforge/store")).expanduser() / "audit.jsonl"
        self.audit = AuditLog(audit_path)

        # 运行时登记表
        self._sandboxes: dict[str, dict] = {}      # id -> {"spec","handle","lifecycle","info"}

    # ------------------------------------------------------------------
    def _make_backend(self, level: str):
        """按隔离等级实例化沙箱后端（process 后端注入 root_dir）。"""
        from ..sandbox import get_backend
        cls = get_backend(level)
        if level == "process":
            return cls(root_dir=self._root)
        return cls()

    # ------------------------------------------------------------------
    @classmethod
    def from_config(cls, config: Config | dict | str | Path | None = None) -> "Substrate":
        """从配置对象 / dict / 路径构建。"""
        if isinstance(config, Config):
            return cls(config)
        if isinstance(config, dict):
            return cls(Config(config))
        return cls(Config(path=config or "config.yaml"))

    # ------------------------------------------------------------------
    def spawn(self, name: str, image: str = "python:3.12", command: list[str] | None = None,
              env: dict | None = None, workdir: str = "/workspace",
              isolation: str = "process", memory_mb: int = 256, cpu_millis: int = 0,
              labels: dict | None = None, **meta) -> SandboxRuntimeInfo:
        """创建并启动一个沙箱。"""
        if name in self._sandboxes:
            raise AlreadyExistsError(f"沙箱已存在: {name}")
        spec = SandboxSpec(
            name=name, image=image, command=command or [], env=env or {},
            workdir=workdir, isolation=IsolationLevel(isolation),
            quota=ResourceQuota(memory_mb=memory_mb, cpu_millis=cpu_millis),
            labels=labels or {}, metadata=meta,
        )
        self.policy.enforce_isolation(spec)
        self.policy.enforce_quota(spec)

        # 按隔离等级取对应后端（可能与默认不同）
        backend = self._make_backend(spec.isolation.value) if spec.isolation.value != self.backend.isolation.value else self.backend
        handle = backend.spawn(spec)

        from ..runtime import Lifecycle
        lc = Lifecycle()
        lc.mark_running()
        info = SandboxRuntimeInfo(
            sandbox_id=name, state=SandboxState.RUNNING, pid=handle.pid,
            isolation=spec.isolation,
        )
        self._sandboxes[name] = {"spec": spec, "handle": handle, "lifecycle": lc, "info": info}
        self.watchdog.beat(name)
        self.audit.record("spawn", sandbox_id=name, isolation=isolation, image=image)
        return info

    def get(self, sandbox_id: str) -> SandboxRuntimeInfo:
        entry = self._sandboxes.get(sandbox_id)
        if entry is None:
            raise NotFoundError(f"沙箱不存在: {sandbox_id}")
        return entry["info"]

    def list_sandboxes(self) -> list[SandboxRuntimeInfo]:
        return [e["info"] for e in self._sandboxes.values()]

    # ------------------------------------------------------------------
    def suspend(self, sandbox_id: str, tags: dict | None = None) -> SnapshotInfo:
        """挂起沙箱：冻结 -> 快照 -> 释放运行环境。"""
        entry = self._require(sandbox_id)
        handle = entry["handle"]
        lc = entry["lifecycle"]

        if lc.state in (SandboxState.SUSPENDED,):
            snap = self.scheduler.snapshot_for(sandbox_id)
            if snap:
                return snap

        lc.mark_suspending()
        t0 = monotonic_ms()
        try:
            handle.backend.pause(handle)
            parent_id = self.scheduler.snapshot_for(sandbox_id).id if self.scheduler.snapshot_for(sandbox_id) else None
            snap = self.snapshot.capture(handle, tags=tags, parent_id=parent_id)
            handle.backend.kill(handle)
        except Exception as exc:
            lc.mark_failed()
            raise SandboxError(f"挂起失败: {exc}") from exc
        elapsed_ms = monotonic_ms() - t0

        lc.mark_suspended()
        self.scheduler.record_suspend(sandbox_id, snap)
        entry["info"].state = SandboxState.SUSPENDED
        snap.meta = {"suspend_ms": elapsed_ms, **snap.meta}
        self.audit.record("suspend", sandbox_id=sandbox_id, snapshot_id=snap.id, ms=elapsed_ms)
        return snap

    def resume(self, sandbox_id: str, snapshot_id: str | None = None) -> SandboxRuntimeInfo:
        """恢复沙箱：从快照重建运行环境（受 resume 预算约束）。"""
        entry = self._require(sandbox_id)
        snap = self.scheduler.snapshot_for(sandbox_id)
        if snap is None:
            raise NotFoundError(f"沙箱 {sandbox_id} 无可用快照，无法恢复")
        if snapshot_id:
            snap = SnapshotInfo(id=snapshot_id, sandbox_id=sandbox_id)

        lc = entry["lifecycle"]
        lc.mark_resuming()
        t0 = monotonic_ms()

        # 还原文件系统到指定目录，并重新拉起进程
        restore_root = self._root / f"{sandbox_id}-resume"
        manifest = self.snapshot.materialize(snap, restore_root)
        spec = entry["spec"]

        backend = self._make_backend(spec.isolation.value)
        try:
            new_handle = backend.spawn(spec)
            new_handle.fs_root = restore_root
        except Exception as exc:
            lc.mark_failed()
            raise SandboxError(f"恢复失败: {exc}") from exc

        elapsed_ms = monotonic_ms() - t0
        entry["handle"] = new_handle
        lc.mark_running()
        entry["info"].state = SandboxState.RUNNING
        entry["info"].pid = new_handle.pid

        # 晋升记录
        self.scheduler.promotion.restore_fn = None
        self.scheduler.promotion.promote(sandbox_id, snap.id)
        self.scheduler.on_access(sandbox_id)
        self.watchdog.beat(sandbox_id)
        self.audit.record("resume", sandbox_id=sandbox_id, snapshot_id=snap.id, ms=elapsed_ms)
        return entry["info"]

    def destroy(self, sandbox_id: str) -> None:
        """销毁沙箱及其运行环境。"""
        entry = self._require(sandbox_id)
        handle = entry["handle"]
        try:
            handle.backend.kill(handle)
        except Exception:
            pass
        entry["lifecycle"].mark_destroyed()
        entry["info"].state = SandboxState.DESTROYED
        self._sandboxes.pop(sandbox_id, None)
        self.watchdog.remove(sandbox_id)
        self.audit.record("destroy", sandbox_id=sandbox_id)

    def list_snapshots(self) -> list[SnapshotInfo]:
        return list(self.scheduler.suspended.values())

    # ------------------------------------------------------------------
    def tick(self) -> list[str]:
        """调度心跳：自动挂起空闲沙箱，超限驱逐。"""
        suspended_now = []
        for sid in self.watchdog.idle_candidates():
            entry = self._sandboxes.get(sid)
            if entry and entry["lifecycle"].state == SandboxState.RUNNING:
                if self.scheduler.should_suspend(self.watchdog.idle_seconds(sid)):
                    self.suspend(sid)
                    suspended_now.append(sid)
        evicted = self.scheduler.evict_if_needed()
        return suspended_now + evicted

    def stats(self) -> SchedulerStats:
        return self.scheduler.stats()

    # ------------------------------------------------------------------
    def _require(self, sandbox_id: str) -> dict:
        entry = self._sandboxes.get(sandbox_id)
        if entry is None:
            raise NotFoundError(f"沙箱不存在: {sandbox_id}")
        return entry

    # ------------------------------------------------------------------
    def demo(self) -> bool:
        """零依赖演示：创建 -> 挂起 -> 恢复 -> 销毁，全程打印。"""
        print("=" * 60)
        print("SubstratForge — 高密度智能体基板 演示")
        print("=" * 60)
        name = f"demo-{new_id()}"
        print(f"\n[1] spawn 沙箱 {name} ...")
        self.spawn(name, image="python:3.12",
                   command=["python", "-c", "import time; time.sleep(86400)"])
        print(f"     状态: {self.get(name).state.value}")

        print("\n[2] suspend 挂起（冻结 -> 快照 -> 释放）...")
        snap = self.suspend(name, tags={"demo": "true"})
        print(f"     快照: {snap.id[:12]}  原始 {snap.size_bytes}B -> 压缩 {snap.compressed_bytes}B")
        print(f"     状态: {self.get(name).state.value}  挂起耗时 {snap.meta.get('suspend_ms')}ms")

        print("\n[3] resume 恢复（从快照重建）...")
        self.resume(name)
        print(f"     状态: {self.get(name).state.value}")
        print(f"     平均恢复 {self.scheduler.stats().avg_resume_ms}ms（预算 {self.scheduler.promotion.resume_budget_ms}ms）")

        print("\n[4] destroy 销毁 ...")
        self.destroy(name)
        print(f"     当前沙箱数: {len(self._sandboxes)}")

        print("\n✅ 演示完成：spawn -> suspend -> resume -> destroy 全链路跑通")
        return True


__all__ = ["Substrate"]
