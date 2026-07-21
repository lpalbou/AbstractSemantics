from __future__ import annotations

import os
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import yaml

# The digest predicate for memory records: every formed record asserts its
# digest text under this predicate (the one CURIE at rest in memory journals;
# decision:0016-vocabulary-direction). Part of the memory-record validation
# set alongside the declared plain-word relations.
MEMORY_DIGEST_PREDICATE = "dcterms:abstract"


@dataclass(frozen=True)
class PredicateDef:
    id: str
    label: Optional[str] = None
    inverse: Optional[str] = None
    description: Optional[str] = None


@dataclass(frozen=True)
class EntityTypeDef:
    id: str
    label: Optional[str] = None
    parent: Optional[str] = None
    description: Optional[str] = None


@dataclass(frozen=True)
class MemoryRelationDef:
    """A memory-record edge relation (AbstractMemory typed records).

    Deliberately a separate vocabulary from `PredicateDef`: memory-record
    relations are engraved as PLAIN WORDS in append-only journals (the
    canonical at-rest spelling, never renamed), while `predicates` feed the
    KG-extraction structured-output enum. `equivalent` carries equal-or-
    broader standard CURIEs as export/interop metadata only — never a second
    at-rest spelling (decision:0016-vocabulary-direction, 2026-07-10).

    `subject_role`/`object_role` (added 2026-07-12) carry the authoritative
    edge DIRECTION in machine-readable form — short role nouns for each
    endpoint (e.g. supports: subject_role="evidence", object_role="claim").
    Writers with caller-asserted endpoints (memory's disposal
    confirm_relation) consume these for direction validation and error
    messages instead of hardcoding a second copy of the semantics.
    """

    id: str
    label: Optional[str] = None
    description: Optional[str] = None
    equivalent: tuple[str, ...] = ()
    subject_role: Optional[str] = None
    object_role: Optional[str] = None


@dataclass(frozen=True)
class SemanticsRegistry:
    version: int
    prefixes: Dict[str, str]
    predicates: List[PredicateDef]
    entity_types: List[EntityTypeDef]
    memory_relations: List[MemoryRelationDef]

    def predicate_ids(self) -> set[str]:
        return {p.id for p in self.predicates if isinstance(p.id, str) and p.id.strip()}

    def entity_type_ids(self) -> set[str]:
        return {t.id for t in self.entity_types if isinstance(t.id, str) and t.id.strip()}

    def memory_relation_ids(self) -> set[str]:
        return {r.id for r in self.memory_relations if isinstance(r.id, str) and r.id.strip()}

    def memory_record_predicate_ids(self) -> set[str]:
        """The full validation set for memory-record writes.

        Declared plain-word relation ids plus the digest predicate — the set
        AbstractMemory's vocabulary validation (its item 0016) checks NEW
        writes against. Engraved history predates validation and is never
        re-checked (append-only journals).
        """
        return self.memory_relation_ids() | {MEMORY_DIGEST_PREDICATE}


def resolve_semantics_registry_path() -> Path:
    """Resolve the registry YAML path.

    Env override:
    - ABSTRACTSEMANTICS_REGISTRY_PATH (relative paths resolve against the
      current working directory; errors always name the resolved path)
    """
    raw = os.getenv("ABSTRACTSEMANTICS_REGISTRY_PATH")
    if isinstance(raw, str) and raw.strip():
        p = Path(raw).expanduser().resolve()
        if not p.exists():
            raise FileNotFoundError(f"ABSTRACTSEMANTICS_REGISTRY_PATH does not exist: {p}")
        if not p.is_file():
            raise FileNotFoundError(f"ABSTRACTSEMANTICS_REGISTRY_PATH is not a file: {p}")
        return p
    return Path(__file__).with_name("semantics.yaml")


def _as_list(value: Any) -> list:
    return list(value) if isinstance(value, list) else []


class _StrictKeyLoader(yaml.SafeLoader):
    """SafeLoader that REFUSES duplicate mapping keys (backlog 0003 item 1).

    PyYAML deliberately does not enforce YAML's unique-key rule: a stray
    pasted second `predicates:` block silently last-wins and can replace the
    whole vocabulary without a sound. For a registry an operator hand-edits,
    that silence is the defect — fail loudly at load instead.
    """


def _strict_mapping(loader: _StrictKeyLoader, node: yaml.nodes.MappingNode, deep: bool = False):
    seen: set = set()
    for key_node, _value_node in node.value:
        # Merge keys (`<<:`) are handled by flatten_mapping inside
        # construct_mapping below; constructing the merge-tag key node here
        # would raise (SafeConstructor has no merge constructor) and refuse
        # valid YAML the old loader accepted. Skip them in the dup scan.
        if key_node.tag == "tag:yaml.org,2002:merge":
            continue
        key = loader.construct_object(key_node, deep=deep)
        # Unhashable keys (lists/dicts) are a YAML error PyYAML raises on its
        # own; only guard hashable duplicates here.
        try:
            duplicate = key in seen
        except TypeError:
            continue
        if duplicate:
            raise ValueError(
                f"duplicate mapping key {key!r} (line {key_node.start_mark.line + 1})"
            )
        seen.add(key)
    return yaml.SafeLoader.construct_mapping(loader, node, deep=deep)


_StrictKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _strict_mapping
)


def _load_yaml(path: Path) -> Dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    try:
        data = yaml.load(raw, Loader=_StrictKeyLoader)
    except yaml.YAMLError as e:
        # PyYAML parses the string and reports '<unicode string>' — the
        # operator hand-editing a registry needs the FILE named.
        raise ValueError(f"Invalid YAML in semantics registry {path}: {e}") from e
    except ValueError as e:
        # Duplicate-key refusal from the strict loader: name the file too.
        raise ValueError(f"Invalid YAML in semantics registry {path}: {e}") from e
    return data if isinstance(data, dict) else {}


def _warn_skips(path: Path, section: str, skipped: int) -> None:
    """ONE warning per section naming path + count (backlog 0003 item 2).

    Item-skip LENIENCY is deliberate for predicates/entity_types (they feed
    enums and fail soft) — but a wrong-indent typo that silently vanishes a
    predicate used to surface only as a distant extractor-enum gap. The load
    succeeds; the operator gets a sound."""
    if skipped:
        warnings.warn(
            f"semantics registry {path}: skipped {skipped} malformed item(s) in "
            f"'{section}' (each must be a mapping with a non-empty string 'id')",
            stacklevel=3,
        )


def load_semantics_registry(path: Path | None = None) -> SemanticsRegistry:
    p = path or resolve_semantics_registry_path()
    data = _load_yaml(p)

    version_raw = data.get("version", 0)
    if version_raw is None:
        # A bare `version:` (explicit null) is absent-shaped, not corrupt —
        # a common hand-edit intermediate; stays quiet like a missing key.
        version_raw = 0
    try:
        version = int(version_raw)
    except Exception:
        # Backlog 0003 item 3: unparseable is DISTINCT from absent — absent
        # defaults quietly, corruption gets a sound (both read as 0).
        warnings.warn(
            f"semantics registry {p}: unparseable version {version_raw!r} — reading as 0",
            stacklevel=2,
        )
        version = 0

    prefixes_raw = data.get("prefixes")
    prefixes: Dict[str, str] = {}
    if isinstance(prefixes_raw, dict):
        for k, v in prefixes_raw.items():
            if isinstance(k, str) and isinstance(v, str) and k.strip() and v.strip():
                prefixes[k.strip()] = v.strip()

    predicates: list[PredicateDef] = []
    skipped = 0
    for item in _as_list(data.get("predicates")):
        if not isinstance(item, dict):
            skipped += 1
            continue
        pid = item.get("id")
        if not isinstance(pid, str) or not pid.strip():
            skipped += 1
            continue
        predicates.append(
            PredicateDef(
                id=pid.strip(),
                label=item.get("label") if isinstance(item.get("label"), str) else None,
                inverse=item.get("inverse") if isinstance(item.get("inverse"), str) else None,
                description=item.get("description") if isinstance(item.get("description"), str) else None,
            )
        )
    _warn_skips(p, "predicates", skipped)

    entity_types: list[EntityTypeDef] = []
    skipped = 0
    for item in _as_list(data.get("entity_types")):
        if not isinstance(item, dict):
            skipped += 1
            continue
        tid = item.get("id")
        if not isinstance(tid, str) or not tid.strip():
            skipped += 1
            continue
        entity_types.append(
            EntityTypeDef(
                id=tid.strip(),
                label=item.get("label") if isinstance(item.get("label"), str) else None,
                parent=item.get("parent") if isinstance(item.get("parent"), str) else None,
                description=item.get("description") if isinstance(item.get("description"), str) else None,
            )
        )
    _warn_skips(p, "entity_types", skipped)

    memory_relations: list[MemoryRelationDef] = []
    skipped = 0
    for item in _as_list(data.get("memory_relations")):
        if not isinstance(item, dict):
            skipped += 1
            continue
        rid = item.get("id")
        if not isinstance(rid, str) or not rid.strip():
            skipped += 1
            continue
        equivalent_raw = item.get("equivalent")
        equivalent = tuple(
            e.strip()
            for e in (equivalent_raw if isinstance(equivalent_raw, list) else [])
            if isinstance(e, str) and e.strip()
        )
        memory_relations.append(
            MemoryRelationDef(
                id=rid.strip(),
                label=item.get("label") if isinstance(item.get("label"), str) else None,
                description=item.get("description") if isinstance(item.get("description"), str) else None,
                equivalent=equivalent,
                subject_role=item.get("subject_role") if isinstance(item.get("subject_role"), str) else None,
                object_role=item.get("object_role") if isinstance(item.get("object_role"), str) else None,
            )
        )
    _warn_skips(p, "memory_relations", skipped)

    # Backlog 0003 item 4: duplicate ids within a section keep FIRST + warn.
    # Set-based consumers were always safe; iterating consumers (enum
    # builders, UI dropdowns) saw both rows and label-wins became
    # consumer-dependent — keep-first makes the winner deterministic.
    def _dedupe(defs, section: str):
        seen: set = set()
        out = []
        dups = []
        for d in defs:
            if d.id in seen:
                dups.append(d.id)
                continue
            seen.add(d.id)
            out.append(d)
        if dups:
            warnings.warn(
                f"semantics registry {p}: duplicate id(s) in '{section}' — "
                f"keeping the first occurrence of: {sorted(set(dups))}",
                stacklevel=3,
            )
        return out

    predicates = _dedupe(predicates, "predicates")
    entity_types = _dedupe(entity_types, "entity_types")

    # memory_relations duplicates are FATAL, not keep-first: this section is
    # load-fatal by doctrine (declaration IS permission), and keep-first would
    # silently decide which of two conflicting role declarations is
    # authoritative — an order-dependent leniency worse than either choice
    # (adversarial finding 2, 2026-07-20).
    rel_ids = [r.id for r in memory_relations]
    rel_dups = sorted({rid for rid in rel_ids if rel_ids.count(rid) > 1})
    if rel_dups:
        raise ValueError(
            f"Semantics registry {p}: duplicate memory relation id(s) {rel_dups} — "
            f"this section is load-fatal; remove the duplicate declaration(s)"
        )

    if not predicates:
        raise ValueError(f"Semantics registry has no predicates: {p}")

    # Structural invariants for memory_relations are enforced at LOAD time —
    # unlike predicates/entity_types (which feed enums and fail soft), a
    # declared memory relation immediately joins memory_record_predicate_ids()
    # whose consumer engraves edges into append-only journals: a config typo
    # would become a permanent at-rest spelling. Load is the only cheap place
    # to fail (declaration IS permission).
    predicate_id_set = {d.id for d in predicates}
    for rel in memory_relations:
        if ":" in rel.id:
            raise ValueError(
                f"Semantics registry {p}: memory relation id {rel.id!r} must be a "
                f"plain word (no CURIE prefix) — plain words are canonical at rest"
            )
        if rel.id in predicate_id_set:
            raise ValueError(
                f"Semantics registry {p}: memory relation id {rel.id!r} collides "
                f"with a KG predicate id — the two vocabularies must stay disjoint"
            )
        if not (rel.subject_role and rel.subject_role.strip()) or not (rel.object_role and rel.object_role.strip()):
            raise ValueError(
                f"Semantics registry {p}: memory relation {rel.id!r} must declare "
                f"both subject_role and object_role (writers validate direction against them)"
            )

    return SemanticsRegistry(
        version=version,
        prefixes=prefixes,
        predicates=predicates,
        entity_types=entity_types,
        memory_relations=memory_relations,
    )


