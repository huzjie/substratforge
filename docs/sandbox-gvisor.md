# gVisor 后端配置

gVisor（runsc）通过拦截 syscall 提供进程级虚拟化，是多租户场景的推荐后端。

## 安装

```bash
# 下载并安装 runsc（以官方 release 为例）
wget https://storage.googleapis.com/gvisor/releases/release/latest/x86_64/runsc
chmod +x runsc && sudo mv runsc /usr/local/bin/
```

## 使用

```yaml
sandbox:
  default_isolation: gvisor
```

`GvisorSandboxBackend` 会自动生成 OCI config.json，挂起/恢复走
`runsc pause/resume`。需准备 rootfs（见 `GvisorSandboxBackend.default_rootfs`）。
