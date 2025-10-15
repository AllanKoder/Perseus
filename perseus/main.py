"""Thin entrypoint for Perseus CLI.

This module intentionally contains minimal logic: configuration and CLI
"""
import click
from perseus.config import ConfigLoader
from perseus.cli import perseus_service
from perseus.cli.perseus_cli import build
from dependency_injector import providers

from perseus.di import Container


@click.group()
@click.option("--config", default=None, help="Path to YAML config file (default: perseus.yaml)")
@click.pass_context
def cli(ctx, config):
    """Perseus CLI: Docs-as-code generator"""
    loader = ConfigLoader(path=config)
    cfg = loader.load()
    ctx.ensure_object(dict)
    ctx.obj["config"] = cfg

    # register configuration in a small DI container for downstream use
    container = Container()

    # container.config expects a mapping-like object; pass the pydantic model
    container.config.from_dict(cfg.model_dump())

    # Ensure the container constructs a PerseusService with the actual
    # Pydantic ConfigData instance (not the raw dict from container.config).
    # TODO: Look into override meaning
    container.perseus_service.override(
        providers.Factory(perseus_service.PerseusService, config=cfg)
    )

    # Wire the CLI module so injection decorators (Provide[...]) resolve to
    # real objects at call time. Also keep the container in ctx as a fallback.
    # TODO: Look into this
    container.wire(modules=["perseus.cli.perseus_cli"])
    ctx.obj["container"] = container

cli.add_command(build)

if __name__ == "__main__":
    cli()
