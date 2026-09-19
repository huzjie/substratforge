# 任务队列与动作处理器

`runtime/task.py` 是内存实现，支持注册任意动作处理器：

```python
q = TaskQueue(workers=4)
q.register_handler("suspend", lambda t: substrate.suspend(t.payload["id"]))
q.start()
task = q.submit("suspend", {"id": "hello"})
```

生产可替换为 Redis/AMQP 后端（保持 `TaskQueue` 接口即可）。
