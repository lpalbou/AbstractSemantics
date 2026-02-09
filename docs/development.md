# Development

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run tests

```bash
pytest
```

Tests are in `tests/` and cover:
- registry loading (`tests/test_registry.py`)
- schema construction and `$ref` resolution (`tests/test_schema.py`)

## Build distributions (sdist + wheel)

```bash
python -m pip install -U build
python -m build
```

Outputs are written to `dist/` (ignored by git via `.gitignore`).

## Regenerate `llms-full.txt`

`llms-full.txt` is a generated “single file context” snapshot for agents. It is generated from `llms.txt` and embeds the contents of all **repository-local** links in that manifest (external links are not embedded). Do not edit `llms-full.txt` manually; edit `llms.txt` and rerun the generator.

```bash
python scripts/generate_llms_full.py
```

## Release checklist (docs-first)

- Update `pyproject.toml` version (and `CHANGELOG.md`)
- Update `src/abstractsemantics/semantics.yaml` (registry changes)
- Ensure docs reflect behavior (`docs/`)
- Run `pytest`
- Build with `python -m build`
- Regenerate `llms-full.txt` (`python scripts/generate_llms_full.py`)

## Related docs

- [Documentation index](README.md)
- [Getting started](getting-started.md)
- [Architecture](architecture.md)
- [Registry format](registry.md)
- [KG assertion JSON Schema](schema.md)
- [FAQ](faq.md)
