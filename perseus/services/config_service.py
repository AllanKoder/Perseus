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
from perseus.helpers.directory import resolve_path

class ConfigService(metaclass=Singleton):
    """Load configuration from YAML and return ConfigData.

    When `path` is None, looks for `perseus.yaml` then `perseus.yml`.
    Stores root directory for downstream usage.
    """

    def __init__(self, root: Optional[str] = None, config_file: Optional[str] = None):
        self.root = root or "."
        self.config_file = config_file
        self.config = self.load()

    def load(self) -> ConfigData:
        candidates = []
        if self.config_file:
            candidates.append(self.config_file)
        else:
            candidates.extend(["perseus.yaml", "perseus.yml"])

        data = {}
        for file in candidates:
            config_path = resolve_path(self.root, file)
            if config_path:
                try:
                    with open(config_path, "r", encoding="utf-8") as fh:
                        data = yaml.safe_load(fh) or {}
                except Exception:
                    data = {}
                break

        config = ConfigData(**(data or {}))
        config.root = self.root
        return config
