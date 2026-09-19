# 内容寻址存储（CAS）升级路径

`snapshot/delta.py` 的块级增量是 rsync 风格的演示实现。生产可用
**内容寻址存储**进一步去重：

- 每个块按 `sha256` 命名存对象，快照只是块的引用列表
- 相同块跨快照 / 跨沙箱自动去重
- 与 Xet 等 CAS 后端（Hugging Face hub v1.32 的本地缓存去重思路一致）对接

见 `storage/s3.py` 的 `_S3Client`，可扩展为对象级 CAS。
