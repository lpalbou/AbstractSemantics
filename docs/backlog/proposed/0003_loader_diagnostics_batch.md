# Proposed: Loader diagnostics batch (duplicate keys, skip warnings, version parse)

## Metadata

- Created: 2026-07-13
- Status: Proposed
- Completed: N/A
- Priority: Low (P2 findings from the 2026-07-13 whole-package fable5 audit;
  the P1s from the same audit shipped same-day — see CHANGELOG)

## Context

The production-readiness audit (2026-07-13) probed the loader with
operator-typo scenarios. The loud failure classes were fixed same-day
(YAML errors name the file; memory_relations invariants enforced at load;
offer-side alias filtering; negative-bounds rejection; py.typed). Four P2
diagnostics remain, all "silent degradation an operator would want a sound
for":

1. **Duplicate top-level YAML keys silently last-win** — PyYAML does not
   enforce the unique-key rule, so a stray pasted `predicates:` block
   replaces 44 predicates without a sound. Fix shape: a small `SafeLoader`
   subclass whose mapping constructor raises on duplicate keys (~10 lines),
   used only by this loader.
2. **Silent item skips have no signal** — a wrong-indent typo turns a
   predicate item into a non-dict and it vanishes; the first symptom is a
   distant extractor enum. Fix shape: count skips per section, emit ONE
   `warnings.warn(...)` naming the path and count.
3. **`version` garbage coerces to 0 silently** — `version: "abc"` reads as
   0, conflating absent with corrupt; `int()` also truncates floats. Fix
   shape: warn on unparseable (distinct from missing).
4. **Duplicate ids within a section are kept** — set-based consumers are
   safe; iterating consumers see both and label-wins becomes
   consumer-dependent. Fix shape: keep-first + warn.

## Promotion criteria

Promote when any operator hand-edits a registry in production, or when the
next loader change touches these code paths anyway.

## Validation ideas

- Duplicate top-level key → ValueError naming the path.
- Malformed item → one warning naming path + section + count; load succeeds.
- `version: "abc"` → warning; version reads 0.
- Duplicate predicate id → first wins; one warning.

## Non-goals

- No behavior change for valid files.
- No strictness for predicates/entity_types beyond warnings (item-skip
  leniency is deliberate — they feed enums and fail soft; only
  memory_relations is load-fatal, shipped 2026-07-13).
