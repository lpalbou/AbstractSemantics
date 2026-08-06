# Completed: Loader diagnostics batch (duplicate keys, skip warnings, version parse)

## Metadata

- Created: 2026-07-13
- Status: Completed
- Completed: 2026-07-20
- Priority: Low (P2 findings from the 2026-07-13 whole-package fable5 audit;
  the P1s from the same audit shipped same-day — see CHANGELOG)

## Context

The production-readiness audit (2026-07-13) probed the loader with
operator-typo scenarios. The loud failure classes were fixed same-day
(YAML errors name the file; memory_relations invariants enforced at load;
offer-side alias filtering; negative-bounds rejection; py.typed). Four P2
diagnostics remained, all "silent degradation an operator would want a sound
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

## Outcome (2026-07-20)

All four diagnostics shipped in `registry.py` (`_StrictKeyLoader`,
`_warn_skips`, version-parse warning, `_dedupe`), promoted by the
framework work dispatch (commons#3815). An adversarial fable5 review over
the build produced two P1 corrections, both folded before receipt:

- **Merge keys (`<<:`) must survive the strict dup scan** — the merge-tag
  key node has no SafeConstructor (it is flattened later inside
  `construct_mapping`); constructing it in the dup scan refused valid YAML
  the old loader accepted. The scan skips merge-tag keys.
- **memory_relations duplicates are FATAL, not keep-first** — keep-first
  ran before the section's structural invariants, so a broken SECOND copy
  demoted a hard load failure to a warning, and conflicting role
  declarations were silently resolved by order. This section is load-fatal
  by doctrine (declaration IS permission); duplicates refuse loudly.

Adversarial P2s folded: explicit `version:` null is absent-shaped (quiet),
matching the "absent defaults quietly" framing. Recorded as deliberate:
duplicate-KEY refusal applies at every nesting level (dup keys are invalid
YAML per spec; syntax errors were always load-fatal — this does not breach
the predicates/entity_types leniency non-goal, which governs ITEM handling);
float versions still truncate silently (in-spec: item 3 warns on
*unparseable* only). Warnings are `UserWarning` via the stdlib `warnings`
module — once-per-call-site dedup means at least one sound per process,
which matches intent.

Validation: `tests/test_registry.py` grew from 22 to 30 tests — one per
diagnostic, plus regression pins for merge keys, null version, fatal
relation duplicates, and a shipped-registry-loads-with-zero-warnings pin
(`simplefilter("error")`) making the "no behavior change for valid files"
non-goal checkable. Adversary re-verified: shipped registry parses equal
old-vs-new, +11% load time (linear), no SafeLoader global pollution.

## Promotion criteria

Promote when any operator hand-edits a registry in production, or when the
next loader change touches these code paths anyway. (Promoted 2026-07-20
under the framework backlog dispatch, commons#3815.)

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
