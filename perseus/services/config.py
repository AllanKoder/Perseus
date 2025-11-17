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
from perseus.services.metaclasses import Singleton
from pydantic import BaseModel, Field


class ConfigData(BaseModel):
    root: str = Field(default=".")
    out: str = Field(default="docs/build")
    format: str = Field(default="md")
    source_exts: List[str] = Field(default_factory=lambda: [".py"])
    pdoc_ext: str = Field(default=".pdoc")
    watch: bool = Field(default=False)
    # list of directory names (or top-level relative paths) to ignore during scans
    ignore_dirs: List[str] = Field(default_factory=list)
    # list of allowed/declared extra fields that may appear inside @pdoc blocks
    # Any extra key present in a block must appear here or the build will fail.
    required_extra_fields: List[str] = Field(default_factory=list)

    class Config:
        extra = "allow"

    @property
    def output_directory(self) -> str:
        """Return the configured output directory resolved relative to `root`.

        If `out` is an absolute path it is returned as-is. Otherwise, the path
        is interpreted as relative to `root` and normalized.
        """
        root_dir = os.path.normpath(self.root)
        out_dir = self.out or ""
        if out_dir and not os.path.isabs(out_dir):
            out_dir = os.path.normpath(os.path.join(root_dir, out_dir))
        return out_dir


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
