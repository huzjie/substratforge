# 教程：从零到密度 1000

## 目标

把 1000 个空闲 agent 停靠到单机，恢复延迟控制在 500ms 内。

## 步骤

### 1. 安装

```bash
pip install .
```

### 2. 配置高密度参数

```yaml
# config.yaml
sandbox:
  default_isolation: process
  max_idle_seconds: 30          # 30 秒空闲即挂起
scheduler:
  max_suspended_per_host: 1000
  resume_budget_ms: 500
snapshot:
  compression: zstd
  delta: true
```

### 3. 批量创建 agent

```python
from substratforge import Substrate

s = Substrate.from_config("config.yaml")
for i in range(1000):
    s.spawn(f"agent-{i}", command=["python", "-c", "import time; time.sleep(86400)"])
```

### 4. 空闲自动挂起

```python
# 主循环里周期性 tick，看门狗会把空闲沙箱逐个挂起
while True:
    s.tick()
    time.sleep(10)
```

### 5. 按需恢复

```python
s.resume("agent-42")   # 从快照恢复，预算 500ms
```

### 6. 观察密度

```python
print(s.stats().as_dict())   # suspended 应接近 1000
```

## 生产提示

- 生产环境建议 `isolation: gvisor`（多租户安全）
- 快照存储接 S3/MinIO 实现跨机恢复
- 见 `docs/benchmarks.md` 了解性能基线
