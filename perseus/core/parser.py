"""Parse YAML text into PdocBlock instances and optionally attach code snippets."""
import yaml
from perseus.models.block import PdocBlock
import re
import textwrap
from typing import List
from perseus.helpers.language import strip_comment_prefixes, Style


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
            # Fallback: try stripping common comment prefixes (handles C-style
            # `*` leaders, //, and #) and re-parse.
            try:
                lines_stripped = strip_comment_prefixes(clean, Style.UNKNOWN)
                data = yaml.safe_load('\n'.join(lines_stripped.splitlines())) or {}
            except Exception:
                data = {}
        if not isinstance(data, dict) or "id" not in data:
            # skip invalid blocks
            continue
        block = PdocBlock(**data)
        parsed.append(block)
    return parsed
