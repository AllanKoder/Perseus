"""Configuration schema and loader for Perseus.

This module defines a Pydantic `ConfigData` model and a `ConfigLoader` that
reads YAML from disk (defaulting to `perseus.yaml` then `perseus.yml`). The
loader returns a validated `ConfigData` instance. This keeps parsing/validation
isolated from CLI logic and follows single-responsibility principles.
"""
import os
from typing import Optional
import yaml
from perseus.models.config_data import ConfigData
from perseus.services.metaclasses import Singleton


class ConfigService:
    """Load configuration from YAML and return ConfigData.

    When `path` is None, looks for `perseus.yaml` then `perseus.yml`.
    """
    __metaclass__ = Singleton

    def __init__(self, path: Optional[str] = None):
        self.path = path
        self.config = self.load()

    def load(self) -> ConfigData:
        candidates = []
        if self.path:
            candidates.append(self.path)
        else:
            candidates.extend(["perseus.yaml", "perseus.yml"])

        data = {}
        for p in candidates:
            if p and os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8") as fh:
                        data = yaml.safe_load(fh) or {}
                except Exception:
                    data = {}
                break

        return ConfigData(**(data or {}))
