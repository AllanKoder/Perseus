"""Render docs from a PerseusContext using Jinja2 templates or export JSON."""

import re
import os
import json
from typing import Any
from jinja2 import Environment, FileSystemLoader, select_autoescape


def build_docs(
    context: Any,
    template_dir: str,
    out_dir: str,
    fmt: str = "md"
) -> str:
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape([]),
    )
    template = env.get_template("default.pdoc")

    os.makedirs(out_dir, exist_ok=True)

    if fmt == "md":
        out: str = template.render(blocks=context.blocks, glossary=context.glossary)
        # Remove trailing spaces from each line and collapse 3+ newlines to 2
        lines = [line.rstrip() for line in out.splitlines()]
        cleaned = "\n".join(lines)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned.strip())

        output_path: str = os.path.join(out_dir, "output.md")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(cleaned)
        return output_path
    elif fmt == "json":
        path: str = os.path.join(out_dir, "output.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"blocks": context.model_dump(), "glossary": context.glossary}, f, indent=2)
        return path
    else:
        raise ValueError(f"Unknown format: {fmt!r}")
