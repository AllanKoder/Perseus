"""Helpers for loading packaged template resources."""
import importlib.resources as resources
from typing import Optional


def get_default_template_content() -> str:
    """Return the packaged default template content as a string.

    Uses importlib.resources so it works when the package is installed as a
    wheel or zip-app.
    """
    # The default is located in the package under `templates/default.pdoc`
    tpl = resources.files("perseus").joinpath("templates").joinpath("default.pdoc")
    return tpl.read_text(encoding="utf-8")
