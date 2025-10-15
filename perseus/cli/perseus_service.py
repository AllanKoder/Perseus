import os
import sys
import click
from dependency_injector.wiring import inject, Provide
from perseus.models.context_model import PerseusContext
from perseus.core import scanner, parser, builder

class PerseusService:
    def __init__(self, config):
        # config is expected to be an instance of ConfigData
        self.config = config

    def build(self):
        root_dir = os.path.normpath(self.config.root)
        out_dir = getattr(self.config, "out_dir", None) or getattr(self.config, "out", None)
        fmt = self.config.format
        exts = self.config.source_exts
        ignore = set(getattr(self.config, "ignore_dirs", []))

        # gather all source text for code extraction heuristics
        # we don't do I/O in the config loader; perform it here
        parts = []
        for dirpath, dirs, files in __import__("os").walk(root_dir):
            # modify `dirs` in-place to skip ignored directories
            dirs[:] = [d for d in dirs if not any(d == ig or __import__("os").path.join(dirpath, d).endswith(ig) for ig in ignore)]
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
            dirs[:] = [d for d in dirs if not any(d == ig or __import__("os").path.join(dirpath, d).endswith(ig) for ig in ignore)]
            for f in files:
                for ext in exts:
                    if f.endswith(ext):
                        path = __import__("os").path.join(dirpath, f)
                        for block_text in scanner.scan_file(path):
                            for b in parser.parse_blocks([block_text], code_text=code_text):
                                # check for any extra keys on the block (fields not in the model)
                                declared_extras = set(getattr(self.config, "required_extra_fields", []))
                                block_dict = b.model_dump() if hasattr(b, "model_dump") else getattr(b, "to_dict", lambda: {})()
                                # model_fields is the pydantic v2 class attribute
                                model_fields = set(getattr(b.__class__, "model_fields", {}).keys())
                                extras = set(block_dict.keys()) - model_fields
                                if extras:
                                    undeclared = extras - declared_extras
                                    if undeclared:
                                        print(f"Syntax error: block '{b.id}' contains undeclared extra fields: {', '.join(sorted(undeclared))}")
                                        sys.exit(1)
                                    # add declared extras into the context (namespace them by block id)
                                    for ex in sorted(extras):
                                        if ex in declared_extras:
                                            val = block_dict.get(ex)
                                            # store under a namespaced key so we don't collide with vocabulary
                                            ctx.glossary[f"{b.id}.{ex}"] = val
                                ctx.add_block(b)
                        break

        template_dir = os.path.normpath(__import__("os").path.join(__import__("os").path.dirname(__file__), "..", "templates"))
        # Ensure output directory exists (will create under project root when relative)
        __import__("os").makedirs(out_dir, exist_ok=True)
        outpath = builder.build_docs(ctx, template_dir, out_dir, fmt=fmt)
        return outpath

    # The CLI integration is handled by the top-level `perseus.main` module which
    # loads a ConfigData and passes it to this class. No click-decorated static
    # helper is necessary here to keep separation of responsibilities.
