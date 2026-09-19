# SubstratForge — 高密度智能体基板运行时

> 把成千上万个空闲 AI 智能体「挂起」成休眠态、需要时在 **亚秒级恢复**，从而在单机上
> 打包比标准容器**高一个数量级**的密度。

[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![CI](https://img.shields.io/badge/CI-passing-brightgreen)](.github/workflows/ci.yml)

SubstratForge 是 Google 2026 年 9 月开源到 GKE 的 **Agent Substrate** 思想的独立开源实现：
一个本地可运行、零外部服务依赖的高密度智能体沙箱运行时。它让「每个智能体独占一个容器」
这种昂贵模式，变成「空闲即挂起、按需亚秒恢复」的**停靠式（parking）调度**。

---

## 为什么需要它

传统做法里，一个长期驻留的智能体（比如浏览器自动化 agent、代码执行 agent）要占住一个
容器 / VM，哪怕它 99% 的时间在等用户输入。成百上千个这样的 agent，成本与内存开销线性
爆炸。

SubstratForge 的做法：

1. **挂起（suspend）**：把空闲 agent 的完整状态（内存元信息 + 文件系统）序列化成**增量快照**落盘，然后释放运行环境
2. **停靠（park）**：单机可「停靠」上千个休眠环境（冷态），只保留少量活跃（热态）环境
3. **恢复（resume）**：请求到达时在 **500ms 预算内**从快照重建运行环境，用户无感

这就是 Agent Substrate 宣称「密度 10 倍」的机制内核。

---

## 核心能力

| 模块 | 说明 |
|---|---|
| **Sandbox** | 三档隔离后端（进程级 / gVisor / microVM），可插拔 |
| **Snapshot** | tar 打包 + 增量（rsync 风格分块）+ zstd/gzip/lz4 压缩 |
| **Scheduler** | 装箱 / 空闲挂起 / 冷停靠驱逐（LRU/LFU/FIFO）/ 冷热晋升 |
| **Storage** | 快照仓库：本地 / S3 / MinIO / 内存，带 GC |
| **Runtime** | 生命周期状态机 + 心跳看门狗 + 任务队列 |
| **Serving** | FastAPI REST + CLI + Python SDK |
| **Observability** | Prometheus 兼容指标 + span 追踪 + 健康检查 |
| **Security** | 最小隔离准入 + 资源配额 + 动作护栏 + 审计日志 |

---

## 快速开始

核心是**零依赖**的，Python 3.9+ 直接跑：

```bash
# 1. 安装（可选，直接 python 也能跑）
pip install .

# 2. 跑一遍挂起/恢复演示
python examples/quickstart.py
# 或
substratforge demo

# 3. 跑密度基准（20 个沙箱逐个挂起/恢复，统计耗时与密度）
python examples/density_bench.py
```

演示输出示意：

```
[1] spawn 沙箱 demo-xxxx ...
     状态: running
[2] suspend 挂起（冻结 -> 快照 -> 释放）...
     快照: snap-xxxx  原始 1024B -> 压缩 512B
     状态: suspended  挂起耗时 12ms
[3] resume 恢复（从快照重建）...
     状态: running
     平均恢复 8.5ms（预算 500ms）
[4] destroy 销毁 ...
     当前沙箱数: 0
✅ 演示完成：spawn -> suspend -> resume -> destroy 全链路跑通
```

---

## 配置

复制 `config.yaml.example` 为 `config.yaml` 后按需修改：

```yaml
sandbox:
  default_isolation: process      # process | gvisor | microvm
  max_idle_seconds: 300           # 空闲多久自动挂起
snapshot:
  compression: zstd               # zstd | gzip | lz4 | none
  delta: true                     # 增量快照
scheduler:
  max_suspended_per_host: 1000    # 单机冷停靠上限
  resume_budget_ms: 500           # 恢复 SLA 预算
storage:
  backend: local                  # local | s3 | minio | memory
```

---

## 三档隔离后端

| 后端 | 启动 | 隔离 | 依赖 | 适用 |
|---|---|---|---|---|
| `process` | ~ms | 进程级（rlimit + 独立进程组） | 无 | 本地开发、可信负载 |
| `gvisor` | ~10ms | syscall 拦截 | 安装 gVisor | 生产默认、多租户 |
| `microvm` | ~50ms | 硬件虚拟化 | 安装 Firecracker | 高安全、不可信代码 |

详见 [`docs/sandbox-gvisor.md`](docs/sandbox-gvisor.md) 与 [`docs/sandbox-microvm.md`](docs/sandbox-microvm.md)。

---

## REST API

```bash
pip install "substratforge[api]"
substratforge serve --config config.yaml
```

```bash
curl -X POST http://127.0.0.1:8080/api/v1/sandboxes \
     -H 'Content-Type: application/json' \
     -d '{"name":"hello","image":"python:3.12","command":["python","-c","import time; time.sleep(86400)"]}'

curl -X POST http://127.0.0.1:8080/api/v1/sandboxes/hello/suspend   # 挂起
curl -X POST http://127.0.0.1:8080/api/v1/sandboxes/hello/resume    # 恢复
curl -X DELETE http://127.0.0.1:8080/api/v1/sandboxes/hello         # 销毁
```

Python SDK（本地 / 远程双模式）：

```python
from substratforge.serving import Client
c = Client(base_url="http://127.0.0.1:8080")
c.spawn({"name": "hello"})
c.suspend("hello")
c.resume("hello")
```

---

## 架构

```
                ┌──────────────────────────────┐
                │         Substrate            │  主引擎 / 编排中枢
                └──────────────┬───────────────┘
        ┌──────────┬───────────┼───────────┬────────────┐
        ▼          ▼           ▼           ▼            ▼
   Sandbox    Snapshot    Scheduler    Storage      Runtime
  (隔离后端)  (快照引擎)   (密度调度)   (快照仓库)   (生命周期/心跳)
        │          │           │           │            │
        └──────────┴─────┬─────┴───────────┴────────────┘
                         ▼
                 Observability + Security
                 (metrics/tracing/audit)
```

详细设计见 [`docs/architecture.md`](docs/architecture.md)。

---

## 目录结构

```
substratforge/
  core/           主引擎 + 注册表
  sandbox/        三档隔离后端 + 网络策略 + 配额
  snapshot/       快照引擎（内存/文件系统/增量/压缩）
  scheduler/      装箱/驱逐/晋升/放置
  storage/        本地/S3/MinIO/内存 + GC
  runtime/        生命周期/心跳/任务队列
  serving/        REST + CLI + SDK
  observability/  metrics/tracing/health
  security/       policy/guardrails/audit
examples/         快速上手 / 密度基准 / 远程 SDK
docs/             架构与设计文档
tests/            pytest 测试
```

---

## 开发

```bash
pip install -e ".[dev]"
pytest -q          # 跑测试
ruff check .       # 静态检查
```

## License

MIT © substratforge contributors。灵感源自 Google Agent Substrate（概念开源），
本实现完全独立，不包含 Google 代码。
