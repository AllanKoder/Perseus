"""Configuration schema for Perseus.

Defines the Pydantic ConfigData model for project configuration.
"""
import logging
import tempfile
from typing import List, Optional
from pydantic import BaseModel, Field
from perseus.helpers.directory import resolve_absolute
from pathlib import Path

class ConfigData(BaseModel):
    root: str = Field(default=".")
    config: str = Field(default="perseus.yaml")
    output: str = Field(default="docs/build")  # Output directory, relative to root unless absolute
    format: str = Field(default="md")
    source_exts: List[str] = Field(default_factory=lambda: [""])
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
        dirs: list[str] = []
        for proj in self.projects:
            r = resolve_absolute(self.root, proj)
            if r is None:
                # Keep behavior explicit: unresolved project entries are skipped here;
                # callers should use `validate_paths()` to ensure correctness.
                continue
            dirs.append(r)
        return dirs

    @property
    def output_directory(self) -> str:
        """
        Return the configured output directory as an absolute path, using self.root.
        """
        res = resolve_absolute(self.root, self.output)
        return str(Path(res)) if res else ""

    @property
    def output_directory_abs(self) -> str:
        """
        Return the configured output directory as an absolute, normalized path.
        """
        res = resolve_absolute(self.root, self.output)
        return str(Path(res)) if res else ""

    @property
    def config_file(self) -> str:
        """
        Return the config file as an absolute path, using self.root.
        """
        res = resolve_absolute(self.root, self.config)
        return str(Path(res)) if res else ""

    @property
    def config_file_abs(self) -> str:
        """
        Return the config file path as an absolute, normalized path.
        """
        res = resolve_absolute(self.root, self.config)
        return str(Path(res)) if res else ""


    def output_subdir_for_template(self, template_dir: str, proj_root: Optional[str]) -> str:
        """
        Given a template directory and the project root that owns it, return the
        appropriate output subdirectory under the configured `output_directory`.

        If `proj_root` is provided and `template_dir` is inside `proj_root`, the
        relative path from `proj_root` to `template_dir` is preserved under the
        `output_directory`. Otherwise the top-level `output_directory` is used.
        """
        out_root = self.output_directory_abs
        out_root_path = Path(out_root) if out_root else Path(self.root).resolve()

        if not proj_root:
            # If no project root was provided this is likely the packaged default
            # template — return the top-level output directory.
            return str(out_root_path)

        proj_root_resolved = resolve_absolute(self.root, proj_root)
        if not proj_root_resolved:
            raise ValueError(f"Could not resolve project root: {proj_root}")
        proj_root_path = Path(proj_root_resolved)

        # Accept both absolute and project-relative template_dir values; resolve accordingly
        if Path(template_dir).is_absolute():
            template_path = Path(template_dir).resolve()
        else:
            template_resolved = resolve_absolute(self.root, template_dir)
            if not template_resolved:
                raise ValueError(f"Could not resolve template directory: {template_dir}")
            template_path = Path(template_resolved)

        # Ensure template is within project root using Path.relative_to
        try:
            # If a file path was provided, use its parent directory so the
            # template filename itself does not become a folder in output.
            candidate = template_path.parent if template_path.is_file() else template_path
            rel = candidate.relative_to(proj_root_path)
        except Exception:
            # Template not in project root — if this is the packaged default
            # template extracted into a temp dir, treat it as intended and
            # silently fall back to top-level output. Otherwise warn so
            # unexpected mismatches are visible.
            tempdir = Path(tempfile.gettempdir())
            try:
                is_temp = template_path.is_relative_to(tempdir)
            except AttributeError:
                # Python <3.9 fallback: fall back to prefix check
                try:
                    is_temp = str(template_path).startswith(str(tempdir))
                except Exception:
                    is_temp = False

            if is_temp or "perseus_templates_" in str(template_path):
                # intended packaged default -> silent fallthrough to top-level output
                return str(out_root_path)

            logging.warning(f"Template directory {template_path} is not inside project root {proj_root_path}; using top-level output directory")
            return str(out_root_path)

        rel_path = rel
        return str(out_root_path.joinpath(rel_path)) if rel_path != Path(".") else str(out_root_path)

    def validate_paths(self) -> None:
        """Validate configured paths and raise explicit errors on problems.

        - Ensures project directories exist and are directories.
        - Ensures config file (if set) resolves to a file.
        - Ensures output directory, if present and exists, is a directory.
        """
        # Validate project directories
        if not self.projects:
            raise ValueError("No project directories configured in 'projects'")

        for proj in self.projects:
            resolved = resolve_absolute(self.root, proj)
            if not resolved:
                raise FileNotFoundError(f"Project directory resolves to empty path: {proj}")
            p = Path(resolved)
            if not p.exists():
                raise FileNotFoundError(f"Project directory not found: {resolved}")
            if not p.is_dir():
                raise NotADirectoryError(f"Project directory is not a directory: {resolved}")

        # Validate config file if present
        cfg_path = resolve_absolute(self.root, self.config)
        if cfg_path:
            p = Path(cfg_path)
            if not p.exists():
                raise FileNotFoundError(f"Config file not found: {cfg_path}")
            if not p.is_file():
                raise FileNotFoundError(f"Config path is not a file: {cfg_path}")

        # Validate output directory if it exists already
        out = resolve_absolute(self.root, self.output)
        if out:
            p = Path(out)
            if p.exists() and not p.is_dir():
                raise NotADirectoryError(f"Configured output path exists and is not a directory: {out}")
