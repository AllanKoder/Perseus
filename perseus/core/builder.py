"""Render docs from a PerseusContext using Jinja2 templates or export JSON."""

import re
from pathlib import Path
import json
from typing import Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template


def build_docs(
    context: Any,
    out_dir: str,
    template_dir: Optional[str],
    template_file: Optional[str],
    fmt: str = "md",
    template_content: Optional[str] = None,
) -> str:
    """Render documentation.

    If `template_content` is provided, it will be used directly as the Jinja2
    template source. Otherwise `template_dir` and `template_file` are used to
    load the template from the filesystem (backwards compatible).
    """
    if template_content is not None:
        template = Template(template_content)
    else:
        # Allow callers to pass either a directory+filename or an absolute
        # path to a template file. If either `template_file` or
        # `template_dir` points to an existing file, read it directly to
        # avoid Jinja2 FileSystemLoader errors when the search path is
        # incorrect (e.g. a file path was supplied instead of a directory).
        tpl_read: Optional[str] = None

        # If template_file is an absolute or relative path to a file, prefer it.
        if template_file:
            tpl_path = Path(template_file)
            if tpl_path.is_file():
                tpl_read = tpl_path.read_text(encoding="utf-8")

        # If not found via template_file, check template_dir in case the
        # caller passed the full path in that parameter.
        if tpl_read is None and template_dir:
            dir_path = Path(template_dir)
            if dir_path.is_file():
                tpl_read = dir_path.read_text(encoding="utf-8")

        # If we were able to read the template from disk, use it. Otherwise
        # fall back to the original FileSystemLoader behavior.
        if tpl_read is not None:
            template = Template(tpl_read)
        else:
            if not template_dir or not template_file:
                raise ValueError("template_dir and template_file are required when template_content is not provided")
            env = Environment(
                loader=FileSystemLoader(template_dir),
                autoescape=select_autoescape([]),
            )
            template = env.get_template(template_file)

    Path(out_dir).mkdir(parents=True, exist_ok=True)

    if fmt == "md":
        out: str = template.render(blocks=context.blocks, glossary=context.glossary)
        # Remove trailing spaces from each line and collapse 3+ newlines to 2
        lines = [line.rstrip() for line in out.splitlines()]
        cleaned = "\n".join(lines)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned.strip())
        out_file_name = f"{Path(template_file or 'default.pdoc').name.replace('.pdoc', '.md')}"
        output_path = Path(out_dir) / out_file_name
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            f.write(cleaned)
        return str(output_path)
    elif fmt == "json":
        out_file_name = f"{Path(template_file or 'default.pdoc').name.replace('.pdoc', '.json')}"
        path = Path(out_dir) / out_file_name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(context.model_dump(), f, indent=2)
        return str(path)
    else:
        raise ValueError(f"Unknown format: {fmt!r}")
