"""Thin entrypoint for Perseus CLI.

This module intentionally contains minimal logic: configuration and CLI
"""
import click
from perseus.cli.perseus_cli import build
from perseus.services.config_service import ConfigService


@click.group()
@click.option("--config", default=None, help="Path to YAML config file (default: perseus.yaml)")
@click.pass_context
def cli(ctx, config):
    ConfigService(config)

cli.add_command(build)

if __name__ == "__main__":
    cli()
