# SubstratForge 运行时镜像（process 后端，零依赖核心 + 可选 API）
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /opt/substratforge

# 复制项目并安装（含可选 API 依赖）
COPY . .
RUN pip install --no-cache-dir ".[api,zstd]" && \
    pip install --no-cache-dir .

EXPOSE 8080 9090

# 默认启动 REST 服务
CMD ["substratforge", "serve", "--config", "config.yaml.example"]
