"""CLI wrapper for Perseus that uses the Config object.

This file exposes a PerseusService class that can be used by a thin `main` module.
"""
import os
import sys
import click
from dependency_injector.wiring import inject, Provide
from perseus.models.context_model import PerseusContext
from perseus.core import scanner, parser, builder
from perseus.di import Container
from perseus.cli.perseus_service import PerseusService


@click.command("build")
@click.option("--root", default=None, help="Root directory to scan for source files")
@click.option("--out", default=None, help="Output directory for generated docs")
@click.option("--format", "-f", default=None, help="Output format: md or json")
@click.option("--ext", default=None, help="Comma-separated source extensions to scan (e.g. .py,.js)")
@click.option("--pdoc-ext", default=None, help="Extension for Perseus doc files (default .pdoc)")
@click.option("--watch", is_flag=True, default=False, help="Enable watch mode (not implemented in demo)")
@inject
def build(root, out, format, ext, pdoc_ext, watch, perseus_service: PerseusService = Provide[Container.perseus_service]):
    """Build docs using a `PerseusService` provided by the DI container."""
    # apply CLI overrides if provided
    overrides = {}
    if root:
        overrides["root"] = root
    if out:
        overrides["out"] = out
    if format:
        overrides["format"] = format
    if ext:
        overrides["source_exts"] = [s.strip() for s in ext.split(",") if s.strip()]
    if pdoc_ext:
        overrides["pdoc_ext"] = pdoc_ext
    if watch:
        overrides["watch"] = True

    # create a merged config if overrides were provided
    cfg = perseus_service.config
    if overrides:
        cfg = cfg.model_copy(update=overrides) if hasattr(cfg, "model_copy") else cfg
        perseus_service = PerseusService(cfg)

    outpath = perseus_service.build()
    click.echo(f"Built: {outpath}")
