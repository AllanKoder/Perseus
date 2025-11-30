"""CLI wrapper for Perseus that uses the Config object.

This file exposes a PerseusService class that can be used by a thin `main` module.
"""
import click
from perseus.services.config_service import ConfigService
from perseus.services.perseus_service import PerseusService

@click.command("build")
@click.option("--projects", default=None, help="Comma-separated list of directories to scan for source files (relative to root)")
@click.option("--output", default=None, help="Output directory for generated docs")
@click.option("--format", "-f", default=None, help="Output format: md or json")
@click.option("--ext", default=None, help="Comma-separated source extensions to scan (e.g. .py,.js)")
@click.option("--pdoc-ext", default=None, help="Extension for Perseus doc files (default .pdoc)")
@click.option("--watch", is_flag=True, default=False, help="Enable watch mode (not implemented in demo)")
def build(projects, output, format, ext, pdoc_ext, watch):
    """Build docs using Pdocs in root project."""
    # apply CLI overrides if provided
    cfg = ConfigService().config
    if output:
        cfg.output = output
    if format:
        cfg.format = format
    if ext:
        cfg.source_exts = [s.strip() for s in ext.split(",") if s.strip()]
    if pdoc_ext:
        cfg.pdoc_ext = pdoc_ext
    if watch:
        cfg.watch = True
    if projects:
        cfg.projects = [d.strip() for d in projects.split(",") if d.strip()]

    perseus_service = PerseusService(cfg)

    outpaths = perseus_service.build()

    for outpath in outpaths:
        click.echo(f"Built: {outpath}")
