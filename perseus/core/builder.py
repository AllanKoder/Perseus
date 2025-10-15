"""Render docs from a PerseusContext using Jinja2 templates or export JSON."""
import os
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape


def build_docs(context, template_dir, out_dir, fmt="md"):
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape([]),
    )
    template = env.get_template("default.pdoc")

    os.makedirs(out_dir, exist_ok=True)

    if fmt == "md":
        out = template.render(blocks=context.blocks, glossary=context.glossary)
        with open(os.path.join(out_dir, "output.md"), "w", encoding="utf-8") as f:
            f.write(out)
        return os.path.join(out_dir, "output.md")
    elif fmt == "json":
        path = os.path.join(out_dir, "output.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"blocks": context.model_dump(), "glossary": context.glossary}, f, indent=2)
        return path
    else:
        raise ValueError("Unknown format: %r" % (fmt,))
