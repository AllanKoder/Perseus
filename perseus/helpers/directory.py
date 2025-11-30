from pathlib import Path
from typing import Optional


def resolve_absolute(root: str, path: str) -> Optional[str]:
    """
    Resolve `path` relative to `root` and return an absolute, normalized path.

    - If `path` is falsy, returns `None`.
    - If `path` is already absolute, returns its normalized absolute form.
    - Otherwise joins it with `root` and returns the normalized absolute path.

    This uses `pathlib.Path.resolve(strict=False)` to normalize without
    requiring the path to exist.
    """
    if not path:
        return None

    root_path = Path(root)
    p = Path(path)

    # If path is not absolute, join with root
    if not p.is_absolute():
        p = root_path.joinpath(p)

    # Normalize (do not require existence)
    try:
        resolved = p.resolve(strict=False)
    except Exception:
        # Fallback to absolute without resolving symlinks
        resolved = p.absolute()

    return str(resolved)
