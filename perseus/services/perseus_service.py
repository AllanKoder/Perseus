import os
import sys
from perseus.models.context_model import PerseusContext
from perseus.core import scanner, parser, builder
from perseus.services.config import ConfigData

class PerseusService:
    """
    Main service for building Perseus documentation from source code and config.
    Handles scanning, parsing, validation, and doc generation.
    """

    def __init__(self, config: None | ConfigData):
        """
        Initialize the service with a config object.
        """
        self.config = config or PerseusService().config


    def build(self):
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
    def _scan_and_parse_blocks(self, ctx, root_dir, exts, ignore):
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

    def _get_output_dir(self):
        """Determine the output directory from config."""
        return getattr(self.config, "out_dir", None) or getattr(self.config, "out", None)


    def _is_ignored(self, dirpath, d, ignore):
        """Check if a directory should be ignored."""
        return any(d == ig or os.path.join(dirpath, d).endswith(ig) for ig in ignore)

    def _validate_and_add_block(self, ctx, block):
        """Validate extra fields and add block to context."""
        declared_extras = set(getattr(self.config, "required_extra_fields", []))
        block_dict = block.model_dump() if hasattr(block, "model_dump") else getattr(block, "to_dict", lambda: {})()
        model_fields = set(getattr(block.__class__, "model_fields", {}).keys())
        extras = set(block_dict.keys()) - model_fields
        if extras:
            undeclared = extras - declared_extras
            if undeclared:
                print(f"Syntax error: block '{block.id}' contains undeclared extra fields: {', '.join(sorted(undeclared))}")
                sys.exit(1)
            for ex in sorted(extras):
                if ex in declared_extras:
                    val = block_dict.get(ex)
                    ctx.glossary[f"{block.id}.{ex}"] = val
        ctx.add_block(block)
