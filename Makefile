PY ?= python

.PHONY: install install-dev demo test lint serve docker

install:
	$(PY) -m pip install .

install-dev:
	$(PY) -m pip install -e ".[api,zstd,dev]"

demo:
	$(PY) examples/quickstart.py

bench:
	$(PY) examples/density_bench.py

test:
	$(PY) -m pytest

lint:
	$(PY) -m ruff check substratforge tests examples

serve:
	$(PY) -m substratforge.serving.cli serve

docker:
	docker build -t substratforge .
	docker compose up -d
