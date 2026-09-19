# 生产级内存快照（CRIU 集成）

当前 `snapshot/mem.py` 提供的是**可演示的元信息捕获**（进程树 / 内存映射 /
打开文件 / 环境）。要获得「进程真实内存的完整镜像」，生产环境应接入
[CRIU](https://criu.org)（Checkpoint/Restore In Userspace）。

## 集成点

`MemoryCapture.capture` 是扩展点：把元信息 JSON 替换为 CRIU 的镜像目录打包即可。

```python
# 伪代码
subprocess.run(["criu", "dump", "-t", str(pid), "-D", img_dir, "--shell-job"])
# 打包 img_dir -> mem_bytes
# 恢复：
subprocess.run(["criu", "restore", "-D", img_dir, "--shell-job"])
```

## 注意事项

- 需要 `CAP_SYS_ADMIN` / root，内核需开启 checkpoint 支持
- 与 gVisor / microVM 后端组合时，通常直接复用其原生快照能力更稳
