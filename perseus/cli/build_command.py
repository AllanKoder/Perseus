"""Command-line entrypoint for Perseus."""
import click
import os
from perseus.models.context_model import PerseusContext
from perseus.core import scanner, parser, builder


def find_source_files(root="."):
    # find .py files for the demo; in a real project this should be configurable
    for dirpath, dirs, files in os.walk(root):
        for f in files:
            if f.endswith(".py"):
                yield os.path.join(dirpath, f)


@click.command("build")
@click.option("--root", default=".")
@click.option("--out", default="docs/build")
@click.option("--format", default="md")
def build_cmd(root, out, format):
    ctx = PerseusContext()
    # gather all source files into one big text for code extraction heuristics
    full_text = []
    for file in find_source_files(root):
        try:
            with open(file, "r", encoding="utf-8") as fh:
                full_text.append(fh.read())
        except Exception:
            continue
    code_text = "\n\n".join(full_text)

    for file in find_source_files(root):
        for block_text in scanner.scan_file(file):
            parsed = parser.parse_blocks([block_text], code_text=code_text)
            for b in parsed:
                ctx.add_block(b)

    outpath = builder.build_docs(ctx, os.path.join(os.path.dirname(__file__), "..", "templates"), out, fmt=format)
    click.echo(f"Built docs to: {outpath}")


if __name__ == "__main__":
    build_cmd()
