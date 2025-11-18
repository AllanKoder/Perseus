import os


def resolve_path(root: str, path: str) -> str:
    """
    Resolve a path relative to root unless it is absolute.
    """
    root_dir: str = os.path.normpath(root)
    if path and not os.path.isabs(path):
        return os.path.normpath(os.path.join(root_dir, path))
    return path
