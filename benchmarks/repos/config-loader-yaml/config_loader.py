# config_loader.py - Typed Configuration Loader with Env Overrides
import os
import yaml
from typing import Dict, Any, Optional


class AppConfig:
    def __init__(self, host: str = "127.0.0.1", port: int = 8080, debug: bool = False, db_url: str = ""):
        self.host = host
        self.port = port
        self.debug = debug
        self.db_url = db_url


class ConfigLoader:
    @staticmethod
    def load_from_dict_and_env(raw_config: Dict[str, Any], env_prefix: str = "APP_") -> AppConfig:
        """
        Load configuration from raw dictionary and apply environment variable overrides.
        Env overrides follow the pattern: {env_prefix}{KEY.upper()}
        For example:
        - APP_PORT=9000 -> overrides port (converted to int)
        - APP_DEBUG=true / APP_DEBUG=1 -> overrides debug (converted to bool)
        - APP_HOST=0.0.0.0 -> overrides host (string)
        - APP_DB_URL=sqlite:///app.db -> overrides db_url (string)
        """
        cfg = dict(raw_config)

        # Apply environment overrides
        # BUG: Doesn't cast types (stores string for port and debug)
        # BUG: Doesn't recognize boolean strings like 'true', '1', 'yes'
        # BUG: Ignores prefix case sensitivity
        for key in ["host", "port", "debug", "db_url"]:
            env_var = f"{env_prefix}{key.upper()}"
            if env_var in os.environ:
                cfg[key] = os.environ[env_var]

        return AppConfig(
            host=cfg.get("host", "127.0.0.1"),
            port=cfg.get("port", 8080),
            debug=cfg.get("debug", False),
            db_url=cfg.get("db_url", "")
        )
