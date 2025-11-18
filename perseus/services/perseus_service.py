import os
import sys
from perseus.models.config_data import ConfigData
from perseus.models.context_model import PerseusContext
from perseus.models.block import PdocBlock
from perseus.core import scanner, parser, builder
from perseus.services.config_service import ConfigService

class PerseusService:
    """
    Main service for building Perseus documentation from source code and config.
    Handles scanning, parsing, validation, and doc generation.
    """

    def __init__(self, config: None | ConfigData):
        """
        Initialize the service with a config object.
        """
        self.config = config or ConfigService().config


    def build(self) -> str:
        """
        Orchestrate the build process: scan, parse, validate, and generate docs.
        Now walks the directory tree only once for efficiency.
        """
        root_dir = os.path.normpath(self.config.root)
        out_dir = self._get_output_dir()
        fmt = self.config.format
        exts = self.config.source_exts
        ignore = set(getattr(self.config, "ignore_dirs", []))

        ctx = PerseusContext()
        self._scan_and_parse_blocks(ctx, root_dir, exts, ignore)
        template_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "templates"))
        os.makedirs(out_dir, exist_ok=True)
        outpath = builder.build_docs(ctx, template_dir, out_dir, fmt=fmt)
        return outpath
    def _scan_and_parse_blocks(self, ctx: PerseusContext, root_dir: str, exts: list[str], ignore: set[str]) -> None:
        """
        Walk the directory tree once, scanning for blocks and parsing each file's content directly.
        Adds blocks to context without accumulating all code in memory.
        """
        for dirpath, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if not self._is_ignored(dirpath, d, ignore)]
            for f in files:
                if any(f.endswith(ext) for ext in exts):
                    path = os.path.join(dirpath, f)
                    for block_text in scanner.scan_file(path):
                        for b in parser.parse_blocks([block_text]):
                            self._validate_and_add_block(ctx, b)

    def _get_output_dir(self) -> str | None:
        """Determine the output directory from config."""
        return getattr(self.config, "out_dir", None) or getattr(self.config, "out", None)


    def _is_ignored(self, dirpath: str, d: str, ignore: set[str]) -> bool:
        """Check if a directory should be ignored."""
        return any(d == ig or os.path.join(dirpath, d).endswith(ig) for ig in ignore)

    def _validate_and_add_block(self, ctx: PerseusContext, block: 'PdocBlock') -> None:
        """Validate extra fields and add block to context."""
        block_dict = block.model_dump()
        model_fields = set(getattr(block.__class__, "model_fields", {}).keys())
        ctx.add_block(block)
