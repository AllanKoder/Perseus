"""Helpers to map file extensions to comment syntaxes (placeholder)."""

COMMENT_SYNTAX = {
    ".py": "#",
    ".js": "//",
    ".java": "//",
    ".go": "//",
}

def get_comment_prefix(path: str) -> str:
    for ext, prefix in COMMENT_SYNTAX.items():
        if path.endswith(ext):
            return prefix
    return "#"
