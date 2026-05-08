# Proposed: Open Question - Should Semantics Extend Beyond Memory

## Metadata
- Created: 2026-05-08
- Status: Proposed
- Completed: N/A

## Context

AbstractSemantics currently defines knowledge-graph vocabulary and KG assertion schemas. That is a
clear and useful role for AbstractMemory and `memory_kg_*` workflows.

The framework also has many other "semantic" concepts:

- Runtime ledger record kinds and status transitions;
- effect types and wait reasons;
- artifact modalities and metadata tags;
- capability readiness states;
- provider/model capability descriptors;
- workflow node types;
- tool approval policy meanings;
- Gateway route and service status payloads.

The open question is whether AbstractSemantics should eventually become the shared home for some of
these cross-package meanings, or whether it should remain narrowly focused on KG/domain semantics.

## Current Code Reality

- Runtime currently owns execution models, effect types, waits, ledgers, and state transitions.
- Gateway currently owns deployment/service readiness and HTTP-facing discovery payloads.
- Core owns provider/model capability registries and generation capability discovery.
- Memory owns triple/query/store contracts.
- Semantics owns KG predicates, entity types, prefixes, and KG assertion schema refs.

There is no current framework-wide semantic registry for ledger records, effects, artifacts, or
capability readiness.

## Problem

The word "semantics" is overloaded. Centralizing every vocabulary in AbstractSemantics might improve
consistency for UIs and validators, but it could also create a package that knows too much about
Runtime, Gateway, Core, and Flow internals.

The biggest risk is coupling: if Semantics starts owning operational behavior or fast-changing
runtime enums, lower-level packages may become harder to evolve and circular dependencies may appear.

The biggest opportunity is consistency: stable schema refs and shared vocabularies could reduce
drift across Gateway, Runtime, Flow, Observer-like tooling, and docs.

## Working Hypothesis

Do not make AbstractSemantics the owner of all framework behavior.

Consider expanding it only into stable, cross-package data vocabularies and schema refs when all of
these are true:

- the vocabulary is used by multiple packages;
- the shape is data-oriented, not behavior-oriented;
- it can be versioned independently;
- it does not require importing Gateway, Runtime, Core, Memory, or Flow;
- it helps validation, documentation, UI generation, or interoperability;
- the owning runtime package can still evolve its implementation without depending on Semantics for
  control flow.

Under this hypothesis:

- KG predicates/entity types stay in Semantics.
- KG assertion schema refs stay in Semantics.
- Artifact modality/tag vocabulary could be a candidate if it becomes cross-package and stable.
- Capability readiness status schema could be a candidate if Gateway/Core/Runtime/Flow need a common
  client contract.
- Ledger record schemas might expose optional schema refs through Semantics, but Runtime should keep
  ownership of ledger models and state-machine behavior.
- Effect types and wait reasons should stay Runtime-owned unless they become a stable external
  interchange contract with explicit versioning.
- Provider/model capabilities should stay Core-owned.
- Auth, CORS, install profiles, and deployment settings should stay out of Semantics.

## Options To Evaluate

Option A: Keep Semantics narrow.

Semantics remains the KG vocabulary/schema package. Other package vocabularies stay local. This is
the safest dependency boundary.

Option B: Expand Semantics into a shared schema-ref and vocabulary package.

Semantics keeps KG ownership and adds carefully selected stable schemas/vocabularies for artifacts,
readiness, or ledger interchange. It still does not own behavior.

Option C: Make Semantics a broad framework ontology.

Semantics becomes the canonical registry for KG, ledger, effects, capabilities, artifacts, workflows,
and policies. This may be attractive conceptually but is likely too much coupling for the current
architecture.

The recommended default is Option B only after concrete evidence appears. Until then, keep Option A.

## Evidence Needed Before Promotion

Promote this question to an ADR or planned work only if at least one concrete drift problem appears:

- Flow, Gateway, Runtime, and Observer-like tools duplicate incompatible ledger/event schemas.
- Thin clients need stable schema refs to render capabilities, artifacts, waits, or ledgers.
- Backlog/ADR review finds repeated confusion about where a vocabulary is owned.
- External integrations need a versioned interchange contract separate from implementation classes.

## Non-Goals

- Do not move Runtime's execution model into Semantics.
- Do not make Semantics import Runtime/Gateway/Core/Memory.
- Do not put provider keys, auth, CORS, model routing, or install-profile behavior in Semantics.
- Do not add hardware or remote-provider extras to Semantics as part of this question.

## Validation Ideas

If promoted, validate with a thin, versioned schema-ref prototype rather than a broad ontology:

- one candidate vocabulary only;
- one producer package;
- one consumer package;
- no new dependency cycle;
- clear owner for behavior remains outside Semantics;
- docs explain why that vocabulary belongs in Semantics rather than the producer package.

## Guidance For Future Agents

Treat this as a strategic question, not a coding task. Before expanding Semantics, map producers,
consumers, versioning, and dependency direction. Prefer a small schema-ref layer over moving live
runtime behavior.
