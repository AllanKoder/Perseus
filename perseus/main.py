"""Thin entrypoint for Perseus CLI.

This module intentionally contains minimal logic: configuration and CLI
behavior are implemented in `perseus.config.ConfigData` / `ConfigLoader` and
`perseus.cli.perseus_cli.PerseusCLI`.
"""
import click
from perseus.config import ConfigLoader
from perseus.cli.perseus_cli import PerseusCLI


@click.group()
@click.option("--config", default=None, help="Path to YAML config file (default: perseus.yaml)")
@click.pass_context
def cli(ctx, config):
    """Perseus CLI group (loads config once and shares it via click.Context.obj)."""
    loader = ConfigLoader(path=config)
    cfg = loader.load()
    ctx.ensure_object(dict)
    ctx.obj["config"] = cfg


@cli.command("build")
@click.option("--root", default=None, help="Root directory to scan for source files")
@click.option("--out", default=None, help="Output directory for generated docs")
@click.option("--format", "-f", default=None, help="Output format: md or json")
@click.option("--ext", default=None, help="Comma-separated source extensions to scan (e.g. .py,.js)")
@click.option("--pdoc-ext", default=None, help="Extension for Perseus doc files (default .pdoc)")
@click.option("--watch", is_flag=True, default=False, help="Enable watch mode (not implemented in demo)")
@click.pass_context
def build(ctx, root, out, format, ext, pdoc_ext, watch):
    cfg = ctx.obj.get("config")
    # collect overrides
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

    merged = cfg.copy(update=overrides) if hasattr(cfg, "copy") else cfg
    cli_obj = PerseusCLI(merged)
    outpath = cli_obj.build()
    click.echo(f"Built: {outpath}")


if __name__ == "__main__":
    cli()
