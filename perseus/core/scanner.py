"""Scan files for @pdoc ... @endp blocks inside any comment type."""
import re
from typing import List

PATTERN = re.compile(r"@pdoc([\s\S]*?)@endp")

def scan_file(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return [m.group(1).strip() for m in PATTERN.finditer(content)]
