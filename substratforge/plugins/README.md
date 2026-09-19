# 插件系统

第三方可通过插件扩展 SubstratForge：

- **沙箱后端**：实现 `SandboxBackend` 并注册到 `backend_registry`
- **驱逐策略**：实现 `evict(entries, limit)` 并注册到 `policy_registry`
- **压缩器**：扩展 `Compressor`
- **存储后端**：实现 `SnapshotStore` 并注册到 `store_registry`

插件发现：`discover_plugins(dir)` 扫描目录，`load_plugin_module` 动态加载，
`PluginManager` 统一调度 `setup()` 完成注册。

```python
from substratforge.plugins import PluginManager
from substratforge.plugins.loader import discover_plugins, load_plugin_module

mgr = PluginManager()
for p in discover_plugins("./my_plugins"):
    mod = load_plugin_module(p)
    mod.setup(mgr)
```
