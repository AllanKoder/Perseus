from pathlib import Path
import importlib.resources as resources
import tempfile

class Constants:
    """Application-wide constants for Perseus."""

    # Absolute path to the built-in templates directory shipped with the package
    DEFAULT_TEMPLATE_DIR: str = str((Path(__file__).resolve().parent / "templates").resolve())

    # Default template filename to use when no project templates found
    DEFAULT_TEMPLATE_FILE: str = "default.pdoc"

    @staticmethod
    def get_default_template_pair() -> tuple[str, str]:
        """
        Ensure the packaged default template is available on the filesystem and
        return a `(directory_path, filename)` pair. This extracts the packaged
        resource into a temporary directory when necessary so callers can treat
        the result as a normal filesystem path.
        """

        # Locate the resource inside the `perseus` package
        templates_pkg = resources.files("perseus").joinpath("templates")
        default_file = templates_pkg.joinpath(Constants.DEFAULT_TEMPLATE_FILE)

        # Read bytes and write to a temporary directory so callers get a real file path
        data = default_file.read_bytes()
        tmpdir = tempfile.mkdtemp(prefix="perseus_templates_")
        out_path = Path(tmpdir) / Constants.DEFAULT_TEMPLATE_FILE
        out_path.write_bytes(data)
        return (str(Path(tmpdir).resolve()), Constants.DEFAULT_TEMPLATE_FILE)
