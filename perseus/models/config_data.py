"""Configuration schema for Perseus.

Defines the Pydantic ConfigData model for project configuration.
"""
import os
from typing import List
from pydantic import BaseModel, Field
from perseus.helpers.directory import resolve_absolute

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
    # Jira configuration (prefer placing these in perseus.yaml)
    jira_base_url: str = Field(default="")
    jira_email: str = Field(default="")
    jira_api_token: str = Field(default="")

    class Config:
        extra = "allow"

    @property
    def project_directories_abs(self) -> list[str]:
        """
        Return the list of project directories as absolute, normalized paths.
        """
        return [resolve_absolute(self.root, proj) for proj in self.projects]

    @property
    def output_directory(self) -> str:
        """
        Return the configured output directory as an absolute path, using self.root.
        """
        return resolve_absolute(self.root, self.output or "")

    @property
    def output_directory_abs(self) -> str:
        """
        Return the configured output directory as an absolute, normalized path.
        """
        return resolve_absolute(self.root, self.output or "")

    @property
    def config_file(self) -> str:
        """
        Return the config file as an absolute path, using self.root.
        """
        return resolve_absolute(self.root, self.config or "")

    @property
    def config_file_abs(self) -> str:
        """
        Return the config file path as an absolute, normalized path.
        """
        return resolve_absolute(self.root, self.config or "")


    def output_subdir_for_template(self, template_dir: str, proj_root: str | None) -> str:
        """
        Given a template directory and the project root that owns it, return the
        appropriate output subdirectory under the configured `output_directory`.

        If `proj_root` is provided and `template_dir` is inside `proj_root`, the
        relative path from `proj_root` to `template_dir` is preserved under the
        `output_directory`. Otherwise the top-level `output_directory` is used.
        """
        out_root = self.output_directory_abs
        if not proj_root:
            return out_root

        # Ensure we compare normalized absolute paths
        proj_root_abs = os.path.normpath(resolve_absolute(self.root, proj_root))
        template_dir_abs = os.path.normpath(template_dir)

        try:
            if os.path.isabs(template_dir_abs) and template_dir_abs.startswith(proj_root_abs):
                rel_path = os.path.relpath(template_dir_abs, proj_root_abs)
                return os.path.join(out_root, rel_path) if rel_path != "." else out_root
        except Exception:
            # Fall back to top-level output directory on any path issues
            return out_root

        return out_root
