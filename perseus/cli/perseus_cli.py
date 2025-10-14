"""CLI wrapper for Perseus that uses the Config object.

This file exposes a PerseusCLI class that can be used by a thin `main` module.
"""
import os
import click
from perseus.models.context_model import PerseusContext
from perseus.core import scanner, parser, builder


class PerseusCLI:
    def __init__(self, config):
        # config is expected to be an instance of ConfigData
        self.config = config

    def build(self):
        root_dir = self.config.root
        out_dir = self.config.out
        fmt = self.config.format if hasattr(self.config, "format") else self.config.format
        exts = self.config.source_exts

        # gather all source text for code extraction heuristics
        # we don't do I/O in the config loader; perform it here
        parts = []
        for dirpath, dirs, files in __import__("os").walk(root_dir):
            for f in files:
                for ext in exts:
                    if f.endswith(ext):
                        path = __import__("os").path.join(dirpath, f)
                        try:
                            with open(path, "r", encoding="utf-8") as fh:
                                parts.append(fh.read())
                        except Exception:
                            pass
                        break
        code_text = "\n\n".join(parts)

        ctx = PerseusContext()
        for dirpath, dirs, files in __import__("os").walk(root_dir):
            for f in files:
                for ext in exts:
                    if f.endswith(ext):
                        path = __import__("os").path.join(dirpath, f)
                        for block_text in scanner.scan_file(path):
                            for b in parser.parse_blocks([block_text], code_text=code_text):
                                ctx.add_block(b)
                        break

        template_dir = os.path.normpath(__import__("os").path.join(__import__("os").path.dirname(__file__), "..", "templates"))
        __import__("os").makedirs(out_dir, exist_ok=True)
        outpath = builder.build_docs(ctx, template_dir, out_dir, fmt=fmt)
        return outpath

    # The CLI integration is handled by the top-level `perseus.main` module which
    # loads a ConfigData and passes it to this class. No click-decorated static
    # helper is necessary here to keep separation of responsibilities.
