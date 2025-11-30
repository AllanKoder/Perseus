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
        s = line.lstrip()
        # Accept either a Style enum or a raw string for backward compatibility
        if not isinstance(style, Style):
            # try to coerce
            try:
                style = Style(style)
            except Exception:
                style = Style.UNKNOWN

        if style == Style.PYTHON:
            # Remove leading '#' and a single space if present
            if s.startswith("#"):
                s = s[1:]
                if s.startswith(" "):
                    s = s[1:]
        elif style == Style.C_LIKE:
            # Remove leading '/*' or '*/' if a caller accidentally included them
            if s.startswith("/*"):
                s = s[2:]
                if s.startswith(" "):
                    s = s[1:]
            if s.startswith("*/"):
                s = s[2:]
                if s.startswith(" "):
                    s = s[1:]
            # Remove leading '*' used in many block-comment styles
            if s.startswith("*"):
                s = s[1:]
                if s.startswith(" "):
                    s = s[1:]
            # Line comments
            if s.startswith("//"):
                s = s[2:]
                if s.startswith(" "):
                    s = s[1:]
        else:
            # Best-effort: strip common single-line comment prefixes
            if s.startswith("#"):
                s = s[1:]
                if s.startswith(" "):
                    s = s[1:]
            elif s.startswith("//"):
                s = s[2:]
                if s.startswith(" "):
                    s = s[1:]
            elif s.startswith("*"):
                s = s[1:]
                if s.startswith(" "):
                    s = s[1:]

        cleaned.append(s)

    # Trim leading/trailing blank lines
    while cleaned and cleaned[0].strip() == "":
        cleaned.pop(0)
    while cleaned and cleaned[-1].strip() == "":
        cleaned.pop()
    return "\n".join(cleaned)
