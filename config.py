import json
import os
from typing import Any, Dict


class AppConfig:
    def __init__(self, data: Dict[str, Any], env: str):
        self._data = data
        self.env = env

    @staticmethod
    def _merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
        out = dict(a)
        for k, v in b.items():
            if isinstance(v, dict) and isinstance(out.get(k), dict):
                out[k] = AppConfig._merge(out[k], v)
            else:
                out[k] = v
        return out

    @staticmethod
    def _validate(cfg: Dict[str, Any]) -> None:
        server = cfg.get("server", {})
        openrouter = cfg.get("openrouter", {})
        if not isinstance(server.get("host", ""), str):
            raise ValueError("server.host must be string")
        if not isinstance(server.get("port", 0), int):
            raise ValueError("server.port must be int")
        if not isinstance(server.get("debug", False), bool):
            raise ValueError("server.debug must be bool")
        if not isinstance(openrouter.get("enabled", True), bool):
            raise ValueError("openrouter.enabled must be bool")
        if not isinstance(openrouter.get("model", ""), str):
            raise ValueError("openrouter.model must be string")
        if not isinstance(openrouter.get("http_referer", ""), str):
            raise ValueError("openrouter.http_referer must be string")
        if not isinstance(openrouter.get("title", ""), str):
            raise ValueError("openrouter.title must be string")
        if openrouter.get("api_key") is not None and not isinstance(openrouter.get("api_key"), str):
            raise ValueError("openrouter.api_key must be string or null")

    @classmethod
    def load(cls) -> "AppConfig":
        env = os.environ.get("APP_ENV", "development").lower()
        with open(os.path.join("config", "config.json"), "r", encoding="utf-8") as f:
            raw = json.load(f)
        base = raw.get("default", {})
        env_cfg = raw.get(env, {})
        cfg = cls._merge(base, env_cfg)
        local_path = os.path.join("config", "config.local.json")
        if os.path.exists(local_path):
            with open(local_path, "r", encoding="utf-8") as f:
                local_raw = json.load(f)
            local_default = local_raw.get("default", {})
            local_env = local_raw.get(env, {})
            cfg = cls._merge(cfg, cls._merge(local_default, local_env))
        cls._validate(cfg)
        return cls(cfg, env)

    def get(self, path: str, default: Any = None) -> Any:
        cur = self._data
        for part in path.split('.'):
            if not isinstance(cur, dict) or part not in cur:
                return default
            cur = cur[part]
        return cur

    def openrouter_api_key(self) -> str:
        return os.environ.get("OPENROUTER_API_KEY") or self.get("openrouter.api_key", "")

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)