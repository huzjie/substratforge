#!/usr/bin/env bash
# 命令行演示（需先 pip install . 或 export PYTHONPATH）
set -e
substratforge demo
substratforge spawn my-sandbox
substratforge suspend my-sandbox
substratforge resume my-sandbox
substratforge stats
substratforge destroy my-sandbox
