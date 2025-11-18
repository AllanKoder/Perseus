"""Configuration schema for Perseus.

Defines the Pydantic ConfigData model for project configuration.
"""
import os
from typing import List
from pydantic import BaseModel, Field
from perseus.helpers.directory import resolve_path

class ConfigData(BaseModel):
    root: str = Field(default=".")
    config: str = Field(default="perseus.yaml")
    output: str = Field(default="docs/build")  # Output directory, relative to root unless absolute
    format: str = Field(default="md")
    source_exts: List[str] = Field(default_factory=lambda: [".py"])
    pdoc_ext: str = Field(default=".pdoc")
    watch: bool = Field(default=False)
    # list of directory names (or top-level relative paths) to ignore during scans
    ignore_dirs: List[str] = Field(default_factory=list)
    # list of project directories to scan (relative to root)
    projects: List[str] = Field(default_factory=lambda: ["."])

    class Config:
        extra = "allow"

    @property
    def project_directories(self) -> list[str]:
        """
        Return the list of project directories as absolute paths, resolved using _resolve_path.
        """
        return [resolve_path(self.root, proj) for proj in self.projects]

    @property
    def output_directory(self) -> str:
        """
        Return the configured output directory as an absolute path, using self.root.
        """
        return resolve_path(self.root, self.output or "")

    @property
    def config_file(self) -> str:
        """
        Return the config file as an absolute path, using self.root.
        """
        return resolve_path(self.root, self.config or "")
