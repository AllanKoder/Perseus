"""Configuration schema and loader for Perseus.

This module defines a Pydantic `ConfigData` model and a `ConfigLoader` that
reads YAML from disk (defaulting to `perseus.yaml` then `perseus.yml`). The
loader returns a validated `ConfigData` instance. This keeps parsing/validation
isolated from CLI logic and follows single-responsibility principles.
"""
from __future__ import annotations
import os
from typing import List, Optional
import yaml
from pydantic import BaseModel, Field


class ConfigData(BaseModel):
    root: str = Field(default=".")
    out: str = Field(default="docs/build")
    format: str = Field(default="md")
    source_exts: List[str] = Field(default_factory=lambda: [".py"])
    pdoc_ext: str = Field(default=".pdoc")
    watch: bool = Field(default=False)

    class Config:
        extra = "allow"


class ConfigLoader:
    """Load configuration from YAML and return ConfigData.

    When `path` is None, looks for `perseus.yaml` then `perseus.yml`.
    """

    def __init__(self, path: Optional[str] = None):
        self.path = path

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
