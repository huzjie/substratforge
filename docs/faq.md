# 常见问题

**Q：核心真的零依赖吗？**
A：是。`substratforge` 包核心只用 Python 标准库，`pip install .` 后可直接跑演示。

**Q：和 Google Agent Substrate 什么关系？**
A：概念对齐（高密度、亚秒恢复），实现完全独立，不包含 Google 代码。

**Q：Windows 上挂起为何不冻结进程？**
A：SIGSTOP/SIGCONT 是 POSIX 特性。Windows 下退化为「快照文件系统 + 元信息，
恢复时重新 spawn」，语义等价，真实进程冻结请用 Linux + gVisor/microVM。

**Q：如何接生产级内存快照？**
A：见 `docs/snapshot-criu.md`（CRIU 集成点）。
