# Contributing

Thanks for your interest in improving `abstractsemantics` — contributions are welcome.

## Quickstart (local dev)

Prerequisites:
- Python `>=3.10` (see `pyproject.toml`)

Setup:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Build distributions:

```bash
python -m pip install -U build
python -m build
```

## What to change

Common contribution areas:

- Registry updates: edit `src/abstractsemantics/semantics.yaml` and ensure docs stay aligned.
- Schema updates: changes to `src/abstractsemantics/schema.py` should come with tests in `tests/`.
- Docs: update `README.md` and `docs/` so external users can understand the package quickly.

## Documentation updates

If you change docs or APIs:

- Update `docs/` and `README.md`.
- Update `CHANGELOD.md`.
- Regenerate `llms-full.txt`:

```bash
python scripts/generate_llms_full.py
```

## Pull request guidelines

- Keep changes focused and small when possible.
- Add/adjust tests for behavior changes.
- Prefer concise, user-facing documentation (start from `docs/getting-started.md`).

