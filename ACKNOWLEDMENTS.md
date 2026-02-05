# Acknowledgments

This project is made possible by the Python ecosystem and a small set of excellent open-source libraries and standards:

## Libraries and tools

- **Python**: language and standard library used throughout (`dataclasses`, `pathlib`, `typing`, …).
- **PyYAML**: YAML parsing used to load the semantics registry (`src/abstractsemantics/registry.py`).
- **pytest**: test runner for the package (`tests/`).
- **setuptools** + **wheel**: packaging/build backend and wheel support (`pyproject.toml`).
- **build**: PEP 517 build frontend used to produce sdists/wheels (`python -m build`; see `docs/development.md`).
- **Mermaid**: diagram syntax used in `docs/architecture.md` (rendering depends on the viewer).

## Standards and vocabularies

- **JSON Schema**: output format produced by `build_kg_assertion_schema_v0()` (`src/abstractsemantics/schema.py`).
- **llms.txt proposal**: guidance for LLM-friendly documentation manifests (see `llms.txt`).
- **Shared vocabularies** referenced by the default registry (`src/abstractsemantics/semantics.yaml`): RDF, Dublin Core Terms (dcterms), Schema.org, SKOS, and CiTO.

Thank you to all maintainers and contributors of these projects and standards.
