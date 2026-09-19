# 贡献指南

1. Fork 仓库，创建分支
2. 安装开发依赖：`pip install -e ".[dev]"`
3. 跑测试与静态检查：`pytest -q && ruff check .`
4. 提交 PR，附上改动说明

新后端 / 策略请优先以**插件**方式提交（见 `substratforge/plugins/`）。
