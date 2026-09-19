# microVM 后端配置（Firecracker）

Firecracker 提供硬件虚拟化级隔离，每个 agent 独占一个轻量 VM。

## 组件

- `vmlinux.bin`：guest kernel
- `rootfs.ext4`：guest 根文件系统

## 启动参数

`MicrovmSandboxBackend(kernel=..., rootfs=...)` 指定路径，生产需配置
boot-source / drive / vsock 网络（骨架已留接口，见 `sandbox/microvm.py`）。
