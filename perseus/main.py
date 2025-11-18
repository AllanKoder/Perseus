"""Thin entrypoint for Perseus CLI.

This module intentionally contains minimal logic: configuration and CLI
"""
import click
from perseus.cli.perseus_cli import build
from perseus.services.config_service import ConfigService
import os



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
