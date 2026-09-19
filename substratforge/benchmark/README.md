# 基准测试框架

- `density.py`：单机可停靠休眠环境数 + 挂起/恢复耗时
- `latency.py`：单沙箱反复挂起/恢复的 p50/p95 延迟
- `throughput.py`：单位时间操作数
- `sla.py`：SLA 预算校验
- `harness.py` / `report.py`：运行器与报告

运行：
```bash
python -m substratforge.benchmark
```
