from __future__ import annotations

import os
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
    - ABSTRACTSEMANTICS_REGISTRY_PATH
    """
    raw = os.getenv("ABSTRACTSEMANTICS_REGISTRY_PATH")
    if isinstance(raw, str) and raw.strip():
        p = Path(raw).expanduser().resolve()
        if not p.exists():
            raise FileNotFoundError(f"ABSTRACTSEMANTICS_REGISTRY_PATH does not exist: {p}")
        return p
    return Path(__file__).with_name("semantics.yaml")


def _as_list(value: Any) -> list:
    return list(value) if isinstance(value, list) else []


def _load_yaml(path: Path) -> Dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw)
    return data if isinstance(data, dict) else {}


def load_semantics_registry(path: Path | None = None) -> SemanticsRegistry:
    p = path or resolve_semantics_registry_path()
    data = _load_yaml(p)

    version_raw = data.get("version", 0)
    try:
        version = int(version_raw)
    except Exception:
        version = 0

    prefixes_raw = data.get("prefixes")
    prefixes: Dict[str, str] = {}
    if isinstance(prefixes_raw, dict):
        for k, v in prefixes_raw.items():
            if isinstance(k, str) and isinstance(v, str) and k.strip() and v.strip():
                prefixes[k.strip()] = v.strip()

    predicates: list[PredicateDef] = []
    for item in _as_list(data.get("predicates")):
        if not isinstance(item, dict):
            continue
        pid = item.get("id")
        if not isinstance(pid, str) or not pid.strip():
            continue
        predicates.append(
            PredicateDef(
                id=pid.strip(),
                label=item.get("label") if isinstance(item.get("label"), str) else None,
                inverse=item.get("inverse") if isinstance(item.get("inverse"), str) else None,
                description=item.get("description") if isinstance(item.get("description"), str) else None,
            )
        )

    entity_types: list[EntityTypeDef] = []
    for item in _as_list(data.get("entity_types")):
        if not isinstance(item, dict):
            continue
        tid = item.get("id")
        if not isinstance(tid, str) or not tid.strip():
            continue
        entity_types.append(
            EntityTypeDef(
                id=tid.strip(),
                label=item.get("label") if isinstance(item.get("label"), str) else None,
                parent=item.get("parent") if isinstance(item.get("parent"), str) else None,
                description=item.get("description") if isinstance(item.get("description"), str) else None,
            )
        )

    memory_relations: list[MemoryRelationDef] = []
    for item in _as_list(data.get("memory_relations")):
        if not isinstance(item, dict):
            continue
        rid = item.get("id")
        if not isinstance(rid, str) or not rid.strip():
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

    if not predicates:
        raise ValueError(f"Semantics registry has no predicates: {p}")

    return SemanticsRegistry(
        version=version,
        prefixes=prefixes,
        predicates=predicates,
        entity_types=entity_types,
        memory_relations=memory_relations,
    )


