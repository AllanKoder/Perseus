"""Helpers to detect language/comment style and normalize comment blocks.

This module provides a simple mapping from file extension to comment
styles and a utility to strip common comment prefixes from an extracted
@pdoc block so YAML inside commented source files can be parsed cleanly.
"""
from pathlib import Path
from typing import Dict
from enum import Enum


class Style(Enum):
    PYTHON = "python"
    C_LIKE = "c_like"
    UNKNOWN = "unknown"


EXT_STYLE_MAP: Dict[str, Style] = {
    # Python: uses `#` and triple-quoted docstrings
    ".py": Style.PYTHON,
    # C-like languages: support /* ... */ block comments and // line comments
    ".c": Style.C_LIKE,
    ".h": Style.C_LIKE,
    ".cpp": Style.C_LIKE,
    ".cc": Style.C_LIKE,
    ".cxx": Style.C_LIKE,
    ".hpp": Style.C_LIKE,
    ".java": Style.C_LIKE,
    ".js": Style.C_LIKE,
    ".ts": Style.C_LIKE,
    ".go": Style.C_LIKE,
    ".rs": Style.C_LIKE,
}


def detect_style_from_path(path: str) -> Style:
    """Return a Style enum inferred from the file extension.

    Falls back to `Style.UNKNOWN` when the extension is not mapped.
    """
    ext = Path(path).suffix.lower()
    return EXT_STYLE_MAP.get(ext, Style.UNKNOWN)


def strip_comment_prefixes(block: str, style: Style) -> str:
    """Strip common comment prefixes from each line of `block` based on `style`.

    - For 'c_like' style we remove leading '*', ' *', and '//' prefixes.
    - For 'python' style we remove leading '#'.
    - For unknown styles we still attempt to remove common markers (#, //, *)

    The function preserves relative indentation inside the block after
    removing comment markers.
    """
    lines = block.splitlines()
    cleaned = []
    for line in lines:
        # Preserve leading indentation so YAML block scalars (|, >)
        # remain correctly indented after stripping comment markers.
        if line.strip() == "":
            cleaned.append("")
            continue

        # number of leading spaces to preserve
        leading_spaces = len(line) - len(line.lstrip(' '))
        tail = line[leading_spaces:]

        # Accept either a Style enum or a raw string for backward compatibility
        if not isinstance(style, Style):
            try:
                style = Style(style)
            except Exception:
                style = Style.UNKNOWN

        if style == Style.PYTHON:
            # Remove a leading '#' after indentation, preserve indentation
            if tail.startswith("#"):
                tail = tail[1:]
                if tail.startswith(" "):
                    tail = tail[1:]
        elif style == Style.C_LIKE:
            # Remove block comment markers or leading '*' used in many C-style
            if tail.startswith("/*"):
                tail = tail[2:]
                if tail.startswith(" "):
                    tail = tail[1:]
            if tail.startswith("*/"):
                tail = tail[2:]
                if tail.startswith(" "):
                    tail = tail[1:]
            if tail.startswith("*"):
                tail = tail[1:]
                if tail.startswith(" "):
                    tail = tail[1:]
            if tail.startswith("//"):
                tail = tail[2:]
                if tail.startswith(" "):
                    tail = tail[1:]
        else:
            # Best-effort: strip common single-line comment prefixes
            if tail.startswith("#"):
                tail = tail[1:]
                if tail.startswith(" "):
                    tail = tail[1:]
            elif tail.startswith("//"):
                tail = tail[2:]
                if tail.startswith(" "):
                    tail = tail[1:]
            elif tail.startswith("*"):
                tail = tail[1:]
                if tail.startswith(" "):
                    tail = tail[1:]

        cleaned.append(" " * leading_spaces + tail)

    # Trim leading/trailing blank lines
    while cleaned and cleaned[0].strip() == "":
        cleaned.pop(0)
    while cleaned and cleaned[-1].strip() == "":
        cleaned.pop()
    return "\n".join(cleaned)
