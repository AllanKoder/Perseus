import os


def resolve_absolute(root: str, path: str) -> str:
    """
    Resolve `path` relative to `root` and return an absolute, normalized path.

    - If `path` is falsy, returns an empty string.
    - If `path` is already absolute, returns its normalized absolute form.
    - Otherwise joins it with `root` and returns the normalized absolute path.
    """
    if not path:
        return ""

    # Normalize and make root absolute first
    root_abs = os.path.abspath(os.path.normpath(root))

    if os.path.isabs(path):
        return os.path.abspath(os.path.normpath(path))

    return os.path.abspath(os.path.normpath(os.path.join(root_abs, path)))
