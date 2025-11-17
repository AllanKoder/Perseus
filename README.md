# Perseus (demo)

Lightweight demo of the Perseus docs-as-code extractor.

Uses UV for package management

Run the demo:

```bash
uv run main.py --config ../test_project/perseus.yaml build --format md
```

This will produce Markdown in `example/docs/output.md`.
