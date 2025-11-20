import os
import sys
import logging
from typing import List
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

    def build(self) -> List[str]:
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
            abs_proj_dir = os.path.abspath(proj_dir)
            logging.debug(f"Scanning project directory for blocks: {abs_proj_dir}")
            self._scan_and_parse_blocks(ctx, abs_proj_dir, exts, ignore)

        templates =  set()  # (directory path, template file name)
        # Scan all the project directories to get all the templates
        for proj_dir in self.config.project_directories:
            abs_proj_dir = os.path.abspath(proj_dir)
            logging.debug(f"Scanning project directory for templates: {abs_proj_dir}")
            self._scan_and_parse_templates(templates, abs_proj_dir)
        # default template if none found
        if not templates:
            logging.debug("No templates found, using default template.")
            templates = set([(os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "templates")), "default.pdoc")])
        
        outpaths: List[str] = []
        os.makedirs(out_dir, exist_ok=True)

        for template_dir, template_file in templates:
            logging.debug(f"Template resolved to: {template_dir}/{template_file}")
            outpath = builder.build_docs(context=ctx, out_dir=out_dir, template_dir=template_dir, template_file=template_file, fmt=fmt)
            logging.debug(f"Documentation built at: {outpath} using format: {fmt} and template: {template_file} from path: {template_dir}")
            outpaths.append(outpath)
        return outpaths

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

    def _scan_and_parse_templates(self, templates: set[tuple[str, str]], proj_dir: str) -> None:
        logging.debug(f"Scanning for templates in directory: {proj_dir}")
        for dirpath, dirs, files in os.walk(proj_dir):
            for f in files:
                if f.endswith(".pdoc"):
                    path = os.path.join(dirpath, f)
                    logging.debug(f"Found template file: {path}")
                    templates.add((dirpath, f))

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
