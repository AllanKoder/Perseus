"""Thin entrypoint for Perseus CLI.

This module intentionally contains minimal logic: configuration and CLI
"""
import logging
import click
from perseus.cli.perseus_cli import build
from perseus.services.config_service import ConfigService
from perseus.env import LOG_LEVEL
import os


# Initialize logging early so debug/info messages are visible even when
# other modules or the environment may have already configured handlers.
_lvl = logging.getLevelName(LOG_LEVEL)
if isinstance(_lvl, str):
    # Unknown names map to strings; fall back to INFO
    _lvl = logging.INFO
root_logger = logging.getLogger()
if not root_logger.handlers:
    logging.basicConfig(level=_lvl)
else:
    # If handlers already exist, ensure the root logger level allows DEBUG messages
    root_logger.setLevel(_lvl)


@click.group()
@click.option("--root", default=".", help="Root directory for resolving all relative paths")
@click.option("--config", default=None, help="Path to YAML config file (relative to root, default: perseus.yaml)")
@click.pass_context
def cli(ctx, root, config):
    # Initialize config singleton and store in context object
    ConfigService(root, config)


cli.add_command(build)

if __name__ == "__main__":
    cli()
