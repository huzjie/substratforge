# -*- coding: utf-8 -*-
from substratforge.config import Config, load_config, DEFAULTS


def test_defaults_merged():
    cfg = load_config("does-not-exist.yaml")
    assert cfg["sandbox"]["default_isolation"] == "process"
    assert cfg["scheduler"]["resume_budget_ms"] == 500


def test_config_get():
    c = Config({"server": {"port": 9999}})
    assert c.get("server.port") == 9999
    assert c.get("server.host", "127.0.0.1") == "127.0.0.1"
