"""Parse YAML text into PdocBlock instances and optionally attach code snippets.

This module now emits debug logging for the cleaned YAML text and any
parsing errors so callers can diagnose why blocks may be skipped.
"""
import logging
import yaml
from perseus.models.block import PdocBlock
import re
import textwrap
from typing import List
from perseus.helpers.language import strip_comment_prefixes, Style

_log = logging.getLogger(__name__)


class ParseError(Exception):
    """Raised when a pdoc block cannot be parsed or validated."""


def parse_blocks(yaml_blocks: List[str], code_text: str = None) -> List[PdocBlock]:
    parsed = []
    for text in yaml_blocks:
        # Normalize indentation and strip surrounding quotes/comment markers.
        clean = textwrap.dedent(text).strip()
        _log.debug("Cleaned block before trimming quotes:\n%s", clean[:1000])
        # If the block is wrapped in triple quotes, remove them
        if clean.startswith('"""') and clean.endswith('"""'):
            clean = clean[3:-3].strip()
        if clean.startswith("'''") and clean.endswith("'''"):
            clean = clean[3:-3].strip()
        _log.debug("Cleaned block after trimming quotes:\n%s", clean[:1000])
        # safe_load may return None if empty
        # If there's any leading non-YAML text (from surrounding docstrings),
        # try to locate the first 'id:' and slice from there.
        id_match = re.search(r"(^|\n)\s*id\s*:", clean)
        if id_match:
            clean = clean[id_match.start():].lstrip('\n')
            _log.debug("Trimmed block to start at 'id:' ->\n%s", clean[:1000])

        try:
            data = yaml.safe_load(clean) or {}
        except yaml.YAMLError as e:
            _log.debug("YAML safe_load failed for cleaned block; attempting fallback strip_comment_prefixes")
            # Fallback: try stripping common comment prefixes (handles C-style
            # `*` leaders, //, and #) and re-parse.
            try:
                lines_stripped = strip_comment_prefixes(clean, Style.UNKNOWN)
                data = yaml.safe_load('\n'.join(lines_stripped.splitlines())) or {}
            except yaml.YAMLError as e2:
                _log.exception("Fallback YAML parsing failed for block:\n%s", clean[:1000])
                raise ParseError(f"YAML parsing failed for block starting with: {clean[:200]!r}") from e2
            except Exception as e2:
                _log.exception("Unexpected error during fallback parsing for block:\n%s", clean[:1000])
                raise ParseError(f"Unexpected error parsing block starting with: {clean[:200]!r}") from e2
        except Exception as e:
            _log.exception("Unexpected exception while parsing block YAML:\n%s", clean[:1000])
            raise ParseError(f"Unexpected error parsing block starting with: {clean[:200]!r}") from e

        # At this point, we must have a mapping/dict with an 'id' key. Treat any
        # deviation as a fatal parsing error (user requested build to halt).
        if not isinstance(data, dict):
            _log.debug("Parsed YAML is not a mapping/dict (error): %r", data)
            raise ParseError(f"Parsed YAML content is not a mapping/dict for block: {clean[:200]!r}")
        if "id" not in data:
            _log.debug("Parsed YAML mapping missing 'id' key (error): %r", data)
            raise ParseError(f"Parsed YAML mapping does not contain required 'id' key for block: {clean[:200]!r}")
        block = PdocBlock(**data)
        parsed.append(block)
    return parsed
