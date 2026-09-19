# 运维手册

- **观察密度**：`substratforge stats` 查看 suspended 数
- **驱逐告警**：suspended 逼近 `max_suspended_per_host` 时关注驱逐
- **恢复 SLA**：`stats().avg_resume_ms` 超 `resume_budget_ms` 时排查存储/后端
- **审计**：`audit.jsonl` 记录 spawn/suspend/resume/destroy
- **快照清理**：定期跑 GC（见 `storage/gc.py`）
