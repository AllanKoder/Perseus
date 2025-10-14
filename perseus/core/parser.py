"""Parse YAML text into PdocBlock instances and optionally attach code snippets."""
import yaml
from perseus.models.block import PdocBlock
import re
import textwrap
from typing import List


def extract_code_near(block_id: str, source_text: str, context_lines: int = 8) -> str:
    """Naive extractor: find function/class with name block_id in source_text and return surrounding lines.
    Falls back to returning an empty string if not found.
    """
    if not source_text:
        return ""
    # simple regex to find a def/class line containing the id
    pattern = re.compile(r"^(.*(?:def|class)\s+" + re.escape(block_id) + r"\b.*)$", re.MULTILINE)
    m = pattern.search(source_text)
    if not m:
        return ""
    # get a window of lines; be conservative about including preceding lines
    lines = source_text.splitlines()
    # find line index of matched line
    for idx, line in enumerate(lines):
        if m.group(1).strip() == line.strip():
            # Start at the def/class line itself. Include decorator lines immediately above it
            s = idx
            while s > 0 and lines[s - 1].lstrip().startswith("@"):
                s -= 1
            # End after a number of context lines to capture body; don't include arbitrary leading docstrings/YAML
            e = min(len(lines), idx + context_lines)
            return "\n".join(lines[s:e]) + "\n"
    return ""


def parse_blocks(yaml_blocks: List[str], code_text: str = None) -> List[PdocBlock]:
    parsed = []
    for text in yaml_blocks:
        # Normalize indentation and strip surrounding quotes/comment markers.
        clean = textwrap.dedent(text).strip()
        # If the block is wrapped in triple quotes, remove them
        if clean.startswith('"""') and clean.endswith('"""'):
            clean = clean[3:-3].strip()
        if clean.startswith("'''") and clean.endswith("'''"):
            clean = clean[3:-3].strip()
        # safe_load may return None if empty
        # If there's any leading non-YAML text (from surrounding docstrings),
        # try to locate the first 'id:' and slice from there.
        id_match = re.search(r"(^|\n)\s*id\s*:", clean)
        if id_match:
            clean = clean[id_match.start():].lstrip('\n')

        try:
            data = yaml.safe_load(clean) or {}
        except yaml.YAMLError:
            # Fallback: try line-by-line stripping leading comment markers
            lines = [l.lstrip('# ').rstrip() for l in clean.splitlines()]
            try:
                data = yaml.safe_load('\n'.join(lines)) or {}
            except Exception:
                data = {}
        if not isinstance(data, dict) or "id" not in data:
            # skip invalid blocks
            continue
        block = PdocBlock(**data)
        if block.code:
            block.code_snippet = extract_code_near(block.id, code_text)
        parsed.append(block)
    return parsed
