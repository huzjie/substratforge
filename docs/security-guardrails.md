# 安全护栏

- **最小隔离准入**：`SecurityPolicy.enforce_isolation` 保证隔离等级不低于配置
- **配额准入**：`enforce_quota` 防止单沙箱超配
- **动作护栏**：`command_whitelist` 等 Guardrail 拦截危险动作
- **审计**：`AuditLog` 以 append-only JSONL 记录 spawn/suspend/resume/destroy

## 示例

```python
from substratforge.security import command_whitelist
g = command_whitelist({"python", "node"})
assert g.allows({"command": ["python", "x.py"]})
assert not g.allows({"command": ["rm", "-rf", "/"]})
```
