# OpenTelemetry 对接

`observability/tracing.py` 提供最小 span 实现。生产对接 OTel：

```python
# 在 Tracer.start/end 里桥接
from opentelemetry import trace
tracer = trace.get_tracer("substratforge")
```

指标侧 `observability/metrics.py` 已输出 Prometheus 文本格式，
可直接被 Prometheus 抓取，无需额外适配。
