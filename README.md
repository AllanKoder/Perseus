# Perseus (demo)

Lightweight demo of the Perseus docs-as-code extractor.

Prereqs (recommended):

Create and activate a virtual environment, then install prerequisites in editable mode:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

This installs the required dependencies from `pyproject.toml` (click, pydantic, jinja2, pyyaml) and creates the `pers` console script.

Run the demo:

```bash
pers build --root example --out example/docs --format md
```

Or directly:

```bash
python3 main.py build --root example --out example/docs --format md
```

This will produce Markdown in `example/docs/output.md`.
