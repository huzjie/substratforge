# 可观测性与安全

- `observability/metrics.py`：Prometheus 兼容指标（零依赖）
- `observability/tracing.py`：span 树，定位挂起/恢复瓶颈
- `observability/health.py`：组件健康检查
- `security/policy.py`：最小隔离等级 + 配额准入
- `security/guardrails.py`：动作护栏（白名单）
- `security/audit.py`：append-only 审计日志
