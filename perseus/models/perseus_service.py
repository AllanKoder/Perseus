import os
import sys
import logging
from perseus.env import LOG_LEVEL
from perseus.models.config_data import ConfigData
from perseus.models.context_model import PerseusContext
from perseus.models.block import PdocBlock
from perseus.core import scanner, parser, builder
from perseus.services.config_service import ConfigService
from perseus.services.metaclasses import Singleton

class PerseusService(metaclass=Singleton):
    """
    Main service for building Perseus documentation from source code and config.
    Handles scanning, parsing, validation, and doc generation.
    """

    def __init__(self, config: None | ConfigData):
        """
        Initialize the service with a config object
        """
        self.config = config or ConfigService().config
        logging.basicConfig(level=LOG_LEVEL)

    def build(self) -> str:
        """
        Orchestrate the build process: scan, parse, validate, and generate docs.
        Now walks the directory tree only once for efficiency.
        """
        out_dir = self.config.output_directory
        fmt = self.config.format
        exts = self.config.source_exts
        ignore = set(getattr(self.config, "ignore_dirs", []))

        logging.debug(f"Output directory resolved to: {out_dir}")
        logging.debug(f"Project directories to scan: {self.config.project_directories}")
        logging.debug(f"Source extensions: {exts}")
        logging.debug(f"Ignore directories: {ignore}")

        ctx = PerseusContext()
        # Scan all project directories, each resolved relative to root
        for proj_dir in self.config.project_directories:
            logging.debug(f"Scanning project directory: {proj_dir}")
            self._scan_and_parse_blocks(ctx, proj_dir, exts, ignore)

        # TODO: Replace with other templates in the future. Do a build for each template we find, instead of just a single step.
        template_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "templates"))
        os.makedirs(out_dir, exist_ok=True)
        logging.debug(f"Template directory resolved to: {template_dir}")

        outpath = builder.build_docs(ctx, template_dir, out_dir, fmt=fmt)
        logging.debug(f"Documentation built at: {outpath}")
        return outpath
    def _scan_and_parse_blocks(self, ctx: PerseusContext, proj_dir: str, exts: list[str], ignore: set[str]) -> None:
        """
        Walk the directory tree once, scanning for blocks and parsing each file's content directly.
        Adds blocks to context without accumulating all code in memory.
        """
        for dirpath, dirs, files in os.walk(proj_dir):
            logging.debug(f"Walking directory: {dirpath}")
            dirs[:] = [d for d in dirs if not self._is_ignored(dirpath, d, ignore)]
            logging.debug(f"Subdirectories after ignore filter: {dirs}")
            for f in files:
                if any(f.endswith(ext) for ext in exts):
                    path = os.path.join(dirpath, f)
                    logging.debug(f"Scanning file: {path}")
                    for block_text in scanner.scan_file(path):
                        for b in parser.parse_blocks([block_text]):
                            logging.debug(f"Parsed block: {b}")
                            self._validate_and_add_block(ctx, b)

    def _is_ignored(self, dirpath: str, d: str, ignore: set[str]) -> bool:
        """Check if a directory should be ignored."""
        result = any(d == ig or os.path.join(dirpath, d).endswith(ig) for ig in ignore)
        if result:
            logging.debug(f"Ignoring directory: {os.path.join(dirpath, d)}")
        return result

    def _validate_and_add_block(self, ctx: PerseusContext, block: 'PdocBlock') -> None:
        """Validate extra fields and add block to context."""
        logging.debug(f"Adding block to context: {block}")
        ctx.add_block(block)
