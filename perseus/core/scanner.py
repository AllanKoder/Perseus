"""Scan files for @pdoc ... @endp blocks inside any comment type."""
import re
import logging
from typing import List

PATTERN = re.compile(r"@pdoc([\s\S]*?)@endp")

def scan_file(path: str) -> List[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        logging.debug(f"Skipping file with non-UTF-8 encoding: {path}")
        return []
    return [m.group(1).strip() for m in PATTERN.finditer(content)]
