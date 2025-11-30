"""Scan files for @pdoc ... @endp blocks inside any comment type.

This scanner now normalizes comment prefixes (e.g. leading '*' in C-style
block comments) so the YAML inside `@pdoc` blocks can be parsed directly.
"""
import re
import logging
from typing import List

from perseus.helpers.language import detect_style_from_path, strip_comment_prefixes

PATTERN = re.compile(r"@pdoc([\s\S]*?)@endp")


def scan_file(path: str) -> List[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        logging.debug(f"Skipping file with non-UTF-8 encoding: {path}")
        return []

    style = detect_style_from_path(path)
    blocks: List[str] = []
    for m in PATTERN.finditer(content):
        raw = m.group(1)
        cleaned = strip_comment_prefixes(raw, style)
        blocks.append(cleaned)
    return blocks
