# Current state

One rolling file. Update `Current work` in place at handoff; do not add dated copies. History lives in git and the linked records.

## Current work

Updated: 2026-10-09 (branch `codex-claude-shared-workflow-20261009`; no push recorded).

Goal: a shared Codex/Claude scientific workflow skill with separate native adapters, checked against measured execution.

Done, with the record that proves it:
- Shared skill, adapters, installer and rollback: `docs/consolidation.md`.
- Ownership, review-packet and progress rules: `docs/efficiency-validation-2026-10-09.md` (38 tests passed).
- Role triggers and milestone review schedule: `docs/trigger-refinement-2026-10-09.md`.
- Calibration preparation: `benchmarks/2026-10-09-calibration/PROTOCOL.md`. Six offline boundary fixtures and the reused 13-test harness.
- Native capture adapter and four-start pilot: `benchmarks/2026-10-09-calibration/RESULTS.md`. Three exact outputs passed; Codex workflow startup failed with service 503. No retries or delegates. Claude workflow cost estimate was 50.44% higher and wall time 9.44% shorter in one pair; no reliable savings/default change established.
- Original pilot completion: 44 repository tests, protected-source/skill/link/instruction checks and one independent Astra review passed. `benchmarks/2026-10-09-calibration/REVIEW.md` preserves limits.
- Post-pilot extraction guidance favors representative schema inspection and scripted scanning; its model-backed effect remains untested.

Dead ends:
- The reused harness cannot test native `scientific_*` roles. Its isolated Claude mode cannot invoke the shared skill, so its results are not workflow evidence.
- The last inspected Claude main was `opus` at high effort (`RUNTIME_REFRESH.json`). Historical Sonnet-main entries describe prior runs; inspect/freeze current settings per comparison.

Current efficiency correction: see [six fixes and evidence](efficiency-corrections.md). The old Claude pair used unequal toolsets and different startup skill/plugin catalogs, so it cannot isolate workflow instructions. Its prices and output checks remain historical observations.

Claude-side checks (2026-10-09, CLI 2.1.296, about $0.55 of a $0.60 cap, Sonnet main unless noted; n=1 each, no old-description comparison): always-on user skill descriptions 2318 characters across 11 model-invocable skills, +38 characters net from today's installs; `settings.json` and Codex config hashes unchanged from recorded values; all five `scientific_*` roles ran on their configured model and effort (explorer haiku/high, reviewer opus/high under Sonnet main; worker and researcher sonnet/medium, analyst sonnet/high under Opus main); CLI `total_cost_usd` equalled the sum of per-model `modelUsage` including the helper model in all three role runs; `/handoff` in a throwaway repo updated the tracked state file, committed only tracked files, left an untracked file alone and made no push; the shortened `scientific-workflow` description fired on 4 of 4 substantial prompts and 0 of 4 trivial ones with only the Skill tool offered. Limits: trivial child tasks, tool set biased toward Skill, Opus main not tested for triggering.

Efficiency corrections: 61 offline tests and required structure, installation, skill and instruction checks passed; independent review: accepted all three corrections; no remaining finding in scope. Corrections checkpointed locally without a push.

Prose-document pilot (prepared 2026-10-09, $0.70 per session cap) was not launched: its fixture is a scriptable control and the adapter now requires a matched peer. Replace it with a task that needs reading or reasoning a script cannot do, in "routing" mode, with a user-set budget (user cap: $2 target, $3 ceiling).

Test plan: [reliability before efficiency](../benchmarks/2026-10-09-calibration/NATIVE_ADAPTER.md#next-test-plan-reliability-before-efficiency), independently reviewed and accepted. A subsequent independent audit reproduced three uncovered defects: surviving owned children after timeout, empty usage accepted as telemetry, and unauthorized helper roles accepted by a count-only check. The earlier 61-test pass and scoped correction review remain valid within their recorded scope; they do not certify these uncovered paths.

Execution record: [test results](../benchmarks/2026-10-09-calibration/TEST_RESULTS.md). Stage A passed independent correction review: 82 workflow tests and 16 isolated runner tests, with red regressions for original defects and a Codex event-conflict defect. The ten-case semantic fixture passed independent truth/scorer inspection; matched preparations passed preflight. Shared-runner recovery branch: `workflow-runner-reliability-20261009`, commit `383b16d`; active scientific branch and unrelated edits preserved.

Next action: resolve the requested budget constraint, then run the prepared native qualification if allowed. No new benchmark parent/helper started. The native cap includes helpers but can overshoot after responses, so it does not prove a strict $3 bound. The user was asked whether to use native estimates with $1 headroom or require a strict pre-request bound; no answer was assumed. Capture qualification, benefit comparison and six prepared later behavioral specifications are unexecuted. Project2 remains paused; no efficiency/default claim.

Open: helper break-even, demanding execution ownership, major-phase review benefit and repeatability remain unmeasured. The four-start pilot was authorized by the user's go-ahead and all four starts ended. Further model-backed calibration needs its own bounded scope/budget; workflow maintenance does not resume Project2.

Boundaries that persist:
- Project2 stays `USER_PAUSED_DO_NOT_RESUME`. No scientific tests, prediction, acquisition, construction or MD.
- Native Claude agents, Codex profiles, settings and the 2026-10-08 benchmark stay unchanged.
- Other sessions' edits and jobs are preserved.

## Open questions

Kept in `skill/scientific-workflow/maintenance.md`, section "Open questions". Not copied here.

## Checks

```sh
python scripts/validate.py
python -m unittest discover -s tests -v
```

Use temporary homes for installer checks. Static checks do not prove live routing or savings.

## Session memory

claude-mem's observer allowance ran out on 2026-10-08, so it records nothing. This file carries state between sessions instead. Skills installed 2026-10-09 (user-level, not in this repo): `handoff`, `wait-what`, `writing-for-agents`, `retro`. Their session-start hook is not installed.
