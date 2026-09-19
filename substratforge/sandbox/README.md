# 沙箱后端

SubstratForge 提供三档可插拔隔离后端，共享同一个 `SandboxBackend` 接口：

| 后端 | 隔离等级 | 启动开销 | 挂起/恢复 | 适用场景 |
|---|---|---|---|---|
| `process` | 进程级 | ~ms | SIGSTOP/SIGCONT | 本地开发、可信负载 |
| `gvisor` | syscall 拦截 | ~10ms | runsc pause/resume | 生产默认、多租户 |
| `microvm` | 硬件虚拟化 | ~50ms | 快照 | 高安全隔离、不可信代码 |

后端通过 `sandbox/__init__.py` 的 `backend_registry` 自动注册，
按 `SandboxSpec.isolation` 取值实例化。详见 `docs/sandbox-*.md`。
