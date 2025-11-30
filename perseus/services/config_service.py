"""Configuration schema and loader for Perseus.

This module defines a Pydantic `ConfigData` model and a `ConfigLoader` that
reads YAML from disk (defaulting to `perseus.yaml` then `perseus.yml`). The
loader returns a validated `ConfigData` instance. This keeps parsing/validation
isolated from CLI logic and follows single-responsibility principles.
"""
from pathlib import Path
from typing import Optional
import yaml
from perseus.models.config_data import ConfigData
from perseus.services.metaclasses import Singleton
from perseus.helpers.directory import resolve_absolute

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
            config_path = resolve_absolute(self.root, file)

            # If user explicitly supplied a config file, fail fast when it's not found
            if self.config_file:
                # config_path may be empty when `file` is falsy; report the original name in that case
                if not config_path or not Path(config_path).exists():
                    raise FileNotFoundError(f"Specified config file not found: {config_path or file}")
                # If the resolved path exists but is not a regular file (e.g. a directory), fail too
                if not Path(config_path).is_file():
                    raise FileNotFoundError(f"Specified config path is not a file: {config_path}")

            # For automatic discovery, skip non-existing candidates or non-files
            if not config_path:
                continue
            p = Path(config_path)
            if not p.exists() or not p.is_file():
                continue

            try:
                with p.open("r", encoding="utf-8") as fh:
                    data = yaml.safe_load(fh) or {}
            except Exception:
                raise IOError(f"Specified config path could not be read: {config_path}")
            break

        # Ensure `root` from the CLI invocation overrides any value in the config file.
        data_combined = dict(data)
        data_combined["root"] = self.root

        # Construct the validated ConfigData with the CLI-root applied (no post-construction mutation).
        config = ConfigData(**data_combined)

        # Validate config paths early and explicitly; let exceptions propagate
        config.validate_paths()

        return config
