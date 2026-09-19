# 服务层

- `api.py`：FastAPI REST（可选依赖，未装则 import 时给出明确提示）
- `cli.py`：命令行工具（零依赖核心即可用 `demo` / `spawn` / `suspend` / `resume`）
- `sdk.py`：Python 客户端，本地 / 远程双模式
- `schemas.py`：pydantic 模型（可选）

启动服务：
```bash
pip install "substratforge[api]"
substratforge serve --config config.yaml
```
