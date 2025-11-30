## Perseus Example Project

This folder demonstrates how to use Perseus to extract and generate documentation from code and narrative `.pdoc` files.

### Structure

- `example/` — Contains sample Python files with embedded `@pdoc` blocks.
- `docs/build/` — Output directory for generated documentation.
- `perseus.yaml` — Configuration files for Perseus.

### How to Run

1. Make sure Perseus and its dependencies are installed (see main project README).
2. Run the build command from the project root:

```bash
uv run perseus/main.py --root test_project/ build
```

3. The generated documentation will appear in `test_project/docs/build/output.md`.

### What to Expect

- Perseus will scan the `example/` directory for Python files and extract any `@pdoc ... @endp` blocks.
- It will merge vocabulary terms into a global glossary.
- The output Markdown will include context, tickets, code snippets, and glossary terms.

### Customization

- Edit `perseus.yaml` to change source paths, output location, or required fields.
- Add more `.pdoc` files or code blocks to expand the documentation.
