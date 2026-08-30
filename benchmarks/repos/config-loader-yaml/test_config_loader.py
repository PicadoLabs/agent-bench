import os
import pytest
from config_loader import ConfigLoader, AppConfig


def test_default_values():
    cfg = ConfigLoader.load_from_dict_and_env({})
    assert cfg.host == "127.0.0.1"
    assert cfg.port == 8080
    assert cfg.debug is False
    assert cfg.db_url == ""


def test_dict_values():
    raw = {"host": "10.0.0.1", "port": 3000, "debug": True, "db_url": "sqlite:///test.db"}
    cfg = ConfigLoader.load_from_dict_and_env(raw)
    assert cfg.host == "10.0.0.1"
    assert cfg.port == 3000
    assert cfg.debug is True
    assert cfg.db_url == "sqlite:///test.db"


def test_env_overrides_with_type_casting(monkeypatch):
    monkeypatch.setenv("APP_PORT", "9999")
    monkeypatch.setenv("APP_DEBUG", "true")
    monkeypatch.setenv("APP_HOST", "0.0.0.0")

    raw = {"host": "localhost", "port": 8080, "debug": False}
    cfg = ConfigLoader.load_from_dict_and_env(raw)

    assert cfg.host == "0.0.0.0"
    assert isinstance(cfg.port, int)
    assert cfg.port == 9999
    assert isinstance(cfg.debug, bool)
    assert cfg.debug is True


def test_boolean_env_string_variations(monkeypatch):
    monkeypatch.setenv("APP_DEBUG", "1")
    cfg1 = ConfigLoader.load_from_dict_and_env({})
    assert cfg1.debug is True

    monkeypatch.setenv("APP_DEBUG", "false")
    cfg2 = ConfigLoader.load_from_dict_and_env({"debug": True})
    assert cfg2.debug is False
