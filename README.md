# Perseus

A documentation extraction and generation system that converts structured comment blocks and narrative `.pdoc` templates into complete Markdown documentation. Perseus centralizes context, vocabulary, and narrative explanation across codebases, keeping documentation maintainable, contextual, and consistent.

---

## Overview

Perseus extracts structured `@pdoc` blocks from code comments, merges them with additional narrative documents, and compiles them into Markdown or JSON outputs using Jinja-style templating.

Key design goals:

* Co-locate documentation context directly with code where it is created.
* Provide richer metadata: intentions, tags, vocabulary definitions, tickets, business requirements, and more.
* Enable narrative documentation that links to code-derived context.
* Support reusable glossary terms across the entire repository.

---

## Core Features

- **Build docs with one command:**
  - Run `perseus build` to scan your codebase and `.pdoc` files, extract context, and generate Markdown docs.
- **Single config file:**
  - Use `perseus.yaml` to set source paths, output location, templates, and format (Markdown, JSON, HTML).
- **Narrative `.pdoc` templates:**
  - Write reusable documentation using Jinja-style syntax, referencing code context and glossary terms.
- **Glossary merging:**
  - All vocabulary from code is merged and available in every doc.

Typical workflow:

1. Add `@pdoc` blocks to your code.
2. Write `.pdoc` templates for narrative docs.
3. Run the build command to generate output.

---

## Components

### 1. Context Blocks (`@pdoc ... @endp`)

Embedded in code comments. These define structured metadata.

Ideal Supported fields (only some implemented currently):

* `intention` – high-level purpose of the unit
* `tickets` – JIRA or other ticket links
* `tags` – searchable identifiers
* `vocabulary` – domain terminology definitions
* `feature_flags`
* `experiments`
* `business_requirement`
* `high_level_intention`
* `prerequisite`
* `approvers`
* `to_do`
* `legacy` / `migration`
* `maintainers`
* `cross_functional_teams`
* `watch` – track file changes (optional)
* `code` – embed relevant code regions (optional)

These fields form the underlying data accessible to `.pdoc` templates.

### 2. Perseus Files (`.pdoc`)

Markdown-like documents with Jinja syntax to assemble final output.

Capabilities:

* Link to context from any file
* Use global glossary
* Render code blocks
* Combine many contexts into a single final document

### 3. Builder / Compiler

The `pers build` compiler performs:

1. Extraction
2. Parsing (YAML)
3. Context storage
4. Template rendering
5. Export to Markdown/JSON/HTML

---


## Technical Implementation

### Directory Scanner
Traverses source paths and locates:
- Code files with `@pdoc` blocks
- `.pdoc` narrative files

### YAML Parser
Uses a fast and accurate YAML parser for blocks within comments.

### Context Repository
A storage layer that collects parsed context and exposes it to the templating engine.

### Template Engine
Uses a Jinja2-compatible engine to render Markdown, JSON, or HTML.

### CLI Interface
The `pers` binary provides:
- `pers build`
- Future commands: `pers watch`, `pers list`, `pers glossary`, etc.

---

## Additional Feature Concepts

### Rich Ticket Context
Supports structured ticket metadata beyond simple strings.

### Tagging
Allows tagging functions, methods, classes, or files for search, indexing, and pattern detection.

### Documentation Design
Teams may choose between:
- Co-located documentation (context embedded next to code)
- Centralized `.pdoc` narrative documents
- A hybrid model
---

## Output Formats
Perseus supports the following output types:
- Markdown (primary)
- JSON (intermediate representation)

Markdown is typically generated from `.pdoc` templates.

---

## Glossary
All vocabulary from every `@pdoc` block is merged into a global glossary.
Every documentation file can reference this glossary.

---

## Quickstart

Install dependencies (recommended: [uv](https://github.com/astral-sh/uv)):

```bash
uv pip install -r requirements.txt
```

Run the demo:

```bash
uv run perseus/main.py --config test_project/perseus.yaml build --format md
```

This will produce Markdown in `test_project/docs/build/output.md`.

## .env

Change the .env for debugging and log levels, use the logger library for logging information over printing
