# Proposed: Semantics Boundary For Runtime, Memory, And Gateway

## Metadata
- Created: 2026-05-08
- Status: Proposed
- Completed: N/A

## Context

AbstractSemantics is currently the lightweight shared vocabulary and schema package for
knowledge-graph assertions. It ships a YAML registry of predicate ids, entity types, and
prefixes, plus helpers for deterministic KG assertion JSON Schemas.

Within the Gateway stack, Semantics is consumed by packages that need stable vocabulary and
validation. It does not run models, serve HTTP endpoints, store memory, execute workflows, or own
provider configuration.

## Current Code Reality

- Base install is already small: `abstractsemantics` depends only on `PyYAML`.
- Optional dependency groups include `dev` plus no-op framework profile aliases:
  `apple`, `gpu`, `all-apple`, and `all-gpu`.
- The registry is package data at `src/abstractsemantics/semantics.yaml`.
- `ABSTRACTSEMANTICS_REGISTRY_PATH` can point to a custom registry file.
- The public schema helper is focused on KG assertion structured outputs.
- The package makes no network calls and has no server, model, storage, GPU, Apple, or remote
  provider behavior.

## Problem

The wider install-profile discussion can create false symmetry. AbstractCore, AbstractVision,
AbstractVoice, Runtime, and Gateway need profile decisions because they may select local engines,
remote endpoints, hardware stacks, or server composition. AbstractSemantics does not have that
kind of runtime surface today.

At the same time, Semantics sits near important boundaries:

- Memory uses semantic predicates and entity types.
- Runtime emits `memory_kg_*` effects and may validate structured KG payloads.
- Gateway can expose readiness and registry information to thin clients.

Without a clear boundary, future work could incorrectly push memory storage, embeddings,
provider/model settings, or operational ledger behavior into Semantics just because the name sounds
global.

## Proposed Direction

Keep AbstractSemantics as the framework's dependency-light vocabulary and schema-reference package.
For the current Gateway stack, its committed role should be:

- own KG predicate/entity vocabulary and prefix definitions;
- own KG assertion schema references and schema builders;
- support custom registry loading through `ABSTRACTSEMANTICS_REGISTRY_PATH`;
- remain importable in lightweight/default installs;
- provide stable data contracts that Memory, Runtime, Gateway, Flow, and tooling can consume.

Do not make Semantics own:

- memory stores;
- vector databases;
- embeddings;
- provider/model settings;
- auth or CORS policy;
- Gateway deployment configuration;
- Runtime execution behavior;
- ledger persistence;
- local/remote/hardware engine selection.

Semantics may later grow beyond KG/memory vocabulary, but only after a separate ADR or promoted
backlog item decides what "framework semantics" means. See
`2026-05-08_semantics_scope_beyond_memory_open_question.md`.

## Installation Profile Boundary

Use simple Semantics profiles:

- `abstractsemantics`: default lightweight runtime package.
- `abstractsemantics[apple]`, `abstractsemantics[gpu]`,
  `abstractsemantics[all-apple]`, and `abstractsemantics[all-gpu]`: no-op compatibility aliases
  for framework-wide profile composition.
- `abstractsemantics[dev]`: tests and development helpers.

Do not add real hardware or provider dependencies unless Semantics later owns hardware- or
provider-specific behavior. Today it should remain a tiny dependency wherever stable KG semantics
are needed.

## Configuration Boundary

Semantics owns:

- default registry location;
- custom registry path resolution;
- registry parsing/validation;
- schema-ref resolution for Semantics-owned schemas.

Gateway may own:

- whether Semantics is installed and ready;
- which registry path was configured for a deployment;
- exposing registry/readiness metadata to clients;
- preflight errors when workflows require KG semantics.

Gateway should not rewrite or synthesize the Semantics registry as part of normal startup. If a
deployment needs an override, it should pass an explicit registry path or config value and report it
in readiness output.

## Pending Changes Guidance

Keep the shared `apple`/`gpu`/`all-*` aliases as no-op compatibility profiles only. If pending
changes attempt to add real hardware/provider dependencies to Semantics, discard that direction
unless a real Semantics-owned optional dependency requires it.

If pending changes attempt to move Memory store selection, embeddings, provider/model defaults, or
Gateway auth/CORS into Semantics, discard that direction. Those are host/runtime responsibilities.

If pending changes attempt to make Semantics the owner of all Runtime ledger/event/effect semantics,
pause and resolve the open question first. Runtime currently owns execution contracts.

## Promotion Criteria

Promote this item when implementing Gateway/Core install-profile work or when Semantics readiness is
needed by Gateway, Flow, or Memory UX.

Promotion should remain small unless the broader scope question has been accepted separately.

## Validation Ideas

- `pip install abstractsemantics` remains dependency-light and imports without Core/Gateway/Runtime.
- Custom `ABSTRACTSEMANTICS_REGISTRY_PATH` still resolves deterministically.
- Runtime/Gateway memory preflight can report Semantics availability without importing storage or
  provider packages.
- KG assertion schema resolution remains deterministic for the default registry.
- Documentation clearly says Semantics is definitions and schemas, not storage or execution.

## Guidance For Implementing Agents

Re-check current code before implementation. Prefer small documentation and readiness changes over
new abstractions. Keep Semantics independent enough that lower packages can import it without
pulling in Gateway, Runtime, Core, Memory, or model-serving dependencies.
