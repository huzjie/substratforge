# -*- coding: utf-8 -*-
"""命令行工具：``substratforge`` 或 ``python -m substratforge.serving.cli``。

子命令：
    serve            启动 REST 服务
    spawn NAME       创建沙箱
    suspend NAME     挂起沙箱
    resume NAME      恢复沙箱
    destroy NAME     销毁沙箱
    list             列出沙箱
    stats            打印调度器统计
    demo             跑一遍挂起/恢复演示（零依赖核心即可）
"""
from __future__ import annotations

import argparse
import json
import sys


def _load_substrate(config_path: str):
    from ..core.substrate import Substrate
    return Substrate.from_config(config_path)


def cmd_serve(args) -> int:
    from ..config import Config
    from .api import create_app
    app = create_app(Config(path=args.config))
    import uvicorn  # type: ignore
    host, port = app.substrate.config.get("server.host", "127.0.0.1"), app.substrate.config.get("server.port", 8080)
    uvicorn.run(app, host=host, port=port)
    return 0


def cmd_spawn(args) -> int:
    s = _load_substrate(args.config)
    h = s.spawn(name=args.name, image=args.image, command=args.command,
                isolation=args.isolation, memory_mb=args.memory_mb)
    print(json.dumps(h.as_dict(), ensure_ascii=False, indent=2))
    return 0


def cmd_suspend(args) -> int:
    s = _load_substrate(args.config)
    snap = s.suspend(args.name)
    print(json.dumps(snap.as_dict(), ensure_ascii=False, indent=2))
    return 0


def cmd_resume(args) -> int:
    s = _load_substrate(args.config)
    h = s.resume(args.name)
    print(json.dumps(h.as_dict(), ensure_ascii=False, indent=2))
    return 0


def cmd_destroy(args) -> int:
    s = _load_substrate(args.config)
    s.destroy(args.name)
    print(f"destroyed {args.name}")
    return 0


def cmd_list(args) -> int:
    s = _load_substrate(args.config)
    for h in s.list_sandboxes():
        print(json.dumps(h.as_dict(), ensure_ascii=False))
    return 0


def cmd_stats(args) -> int:
    s = _load_substrate(args.config)
    print(json.dumps(s.scheduler.stats().as_dict(), ensure_ascii=False, indent=2))
    return 0


def cmd_demo(args) -> int:
    from ..core.substrate import Substrate
    s = Substrate.from_config(args.config)
    return 0 if s.demo() else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="substratforge", description="高密度智能体基板运行时")
    p.add_argument("--config", default="config.yaml")
    sub = p.add_subparsers(dest="cmd")

    sp = sub.add_parser("serve", help="启动 REST 服务")
    sp.set_defaults(fn=cmd_serve)

    sp = sub.add_parser("spawn", help="创建沙箱")
    sp.add_argument("name")
    sp.add_argument("--image", default="python:3.12")
    sp.add_argument("--command", nargs="*", default=[])
    sp.add_argument("--isolation", default="process")
    sp.add_argument("--memory-mb", type=int, default=256)
    sp.set_defaults(fn=cmd_spawn)

    for name in ("suspend", "resume", "destroy"):
        sp = sub.add_parser(name, help=f"{name} 沙箱")
        sp.add_argument("name")
        sp.set_defaults(fn=globals()[f"cmd_{name}"])

    sp = sub.add_parser("list", help="列出沙箱")
    sp.set_defaults(fn=cmd_list)

    sp = sub.add_parser("stats", help="打印调度统计")
    sp.set_defaults(fn=cmd_stats)

    sp = sub.add_parser("demo", help="跑挂起/恢复演示")
    sp.set_defaults(fn=cmd_demo)
    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "cmd", None):
        parser.print_help()
        return 1
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
