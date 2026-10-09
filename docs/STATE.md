# Current state

One rolling file. Update `Current work` in place at handoff; do not add dated copies. History lives in git and the linked records.

## Current work

Updated: 2026-10-09, fresh-session handoff (branch `codex-claude-shared-workflow-20261009`; no push recorded).

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

Live-plan next action: resolve the requested budget constraint, then run the prepared native qualification if allowed. Latest evaluation priority: bounded historical-session analysis before further paid benefit trials; this has been recommended, not executed. No new benchmark parent/helper started under the prepared allocation. The native cap includes helpers but can overshoot after responses, so it does not prove a strict $3 bound. The user was asked whether to use native estimates with $1 headroom or require a strict pre-request bound; no answer was assumed. Capture qualification, benefit comparison and six prepared later behavioral specifications are unexecuted. Project2 remains paused; no efficiency/default claim.

Evaluation discussion: see [interpretation and next evaluation](../benchmarks/2026-10-09-calibration/TEST_RESULTS.md#interpretation-and-next-evaluation-after-claude-side-checks). No universal token penalty or hours-based benefit is established. Prioritize bounded historical-session analysis before further paid benefit trials. Optional opt-in requires native invocation controls and auditing instruction routes; no settings or agents were changed.

Open: helper break-even, demanding execution ownership, major-phase review benefit and repeatability remain unmeasured. The four-start pilot was authorized by the user's go-ahead and all four starts ended. Further model-backed calibration needs its own bounded scope/budget; workflow maintenance does not resume Project2.

Boundaries that persist:
- Project2 stays `USER_PAUSED_DO_NOT_RESUME`. No scientific tests, prediction, acquisition, construction or MD.
- Native Claude agents, Codex profiles, settings and the 2026-10-08 benchmark stay unchanged.
- Other sessions' edits and jobs are preserved.


## Fresh-session continuation

Start a new Codex or Claude session in `~/githubrepo/scientific-workflow-skill`. Changing the working directory inside the old session would retain its long RNA-project context. Read this file and repository `AGENTS.md` first, then the linked plan/results only as needed. This file is the rolling handoff; keep the test plan and detailed evidence at their existing paths.

The user wants reliable long-task execution and better accepted results at reasonable whole-task cost. They originally requested small models for repetitive work and stronger models for demanding work and major project decisions. The corrections now require delegation to replace identified owner work. Duration, file count or a smaller helper model alone does not justify a team.

### Exact starting point and checkpoints

Last source checkpoint before this handoff: `61184ef` (delegation-economics interpretation). Earlier checkpoints: `d989d8c` (Claude's additional checks), `cc93787` (harness fixes and prepared fixture), `027d125` (reviewed test plan), `dfe47fd` (six efficiency corrections), and `5ee26a0` (Claude's restored scientific-evidence paragraph). Preserve all of them. This handoff will be checkpointed separately; find its identity with `git log -1 --oneline`.

The working tree was clean when handoff preparation began. Recheck it and any active session before editing. Native-role smoke checks and independent Stage A review are complete; do not repeat them for unchanged inputs. The 82-test workflow pass and 16-test runner pass certify their tested paths, not live permission enforcement, scientific success or savings.

The shared runner is an external dependency at `/home/hao/githubrepo/sequence_design/tools/workflow_evaluation/run.py`. Its two-file correction is checkpointed at `383b16d3998022b77d3630ed04005494c02260a9` on `workflow-runner-reliability-20261009`, with a clean recovery worktree at `/tmp/workflow-runner-checkpoint` when inspected. Corrections were also applied to the canonical runner; that repository's `dev` contains other sessions' work. Do not merge, revert or run its broad suite automatically. The absolute runner dependency and children escaping the owned process group remain limits to consider if those questions become relevant.

### Next work and completion criteria

1. **Reconstruct current authority and ownership.** Inspect this repo's branch, working tree and current state. Preserve any new Claude edits and running jobs. Project2 remains paused; this workflow handoff does not authorize its execution. Do not reactivate old workers from the previous project.
2. **Prioritize a bounded retrospective before proposing more paid trials.** Select and document a small set of existing successful and failed long sessions across both runtimes. Use scripts for transcript counts and inspect only decision-relevant excerpts. Separate active turns from solver/tool waiting; parent and child work; new/cached input and output; setup and recurring task costs. Track compactions, repeated reads, redundant reviews/checks, errors, drift, accepted artifacts and recovery. Missing telemetry stays unknown. Finish with trace-backed findings and a concrete testable hypothesis; historical associations cannot establish counterfactual savings. No retrospective has been executed yet, and no sampling plan is frozen. Avoid building another reporting framework.
3. **If a policy change is requested, stage it away from live links.** Optional opt-in is a recommendation, not an implemented or authorized settings change. Audit instruction routes as well as skill metadata. Current global Codex guidance requires this skill for substantial scientific tasks; metadata alone would not remove that route. Keep project-required gates and native agents intact. Verify affected explicit invocation and routine restraint only; reuse unchanged dispatch evidence. Do not promise zero context overhead.
4. **Keep live work behind its existing gates.** Once the budget interpretation is resolved, revalidate or regenerate frozen preparations as needed, then run one qualification before any comparison. The small semantic pair is a capture/integration diagnostic. Substantial independent-retrieval and dependent-implementation comparisons, repetition and hours-long trials need their own frozen design and allocation. A failed or invalid observation is retained; it does not authorize a retry.
5. **Complete only the named checks and local checkpoint for the scoped change.** For handoff/prose-only edits, check changed links, fences, structure and whitespace. Implementation/routing changes require the repository's documented tests and checks. Do not repeat a full passing suite for unchanged code. No push without user authority.

### Unresolved live gate: do not infer an answer

The user-set pilot budget is a $2 target and $3 ceiling. The outstanding clarification is whether to accept reported native session limits with $1 headroom, or require a strict pre-request aggregate bound. No answer has been received. Claude's `--max-budget-usd` includes helper estimates but is checked after a response and may overshoot. A timeout does not enforce a dollar ceiling. Coordinator/reviewer spend is unknown and outside the proposed recorded family scope; do not claim complete project spend.

The proposed initial allocation is three parent starts and two helper starts total, one parent family at a time: $0.40 qualification and $0.80 per arm, each with a 300-second deadline plus bounded cleanup. No starts were used in this allocation. The reserve is not retry authority. Claude's separate completed routing/trigger/handoff checks used about $0.55 of their separately recorded $0.60 cap; do not silently merge allocations.

Qualification acceptance must explicitly establish native identity, effective allowed/denied permissions, family accounting and cleanup. The adapter deliberately records `qualification_gate.accepted: false` until that evidence is assessed. Passing exact output/capture tests alone does not lift this gate. Only then may a matched pair run. Initial differences stay descriptive; general savings/default claims need representative held-out evidence.

### Resume assets and where to read

| Need | Existing source |
| --- | --- |
| Active staged test plan and stopping rules | [NATIVE_ADAPTER.md](../benchmarks/2026-10-09-calibration/NATIVE_ADAPTER.md#next-test-plan-reliability-before-efficiency) |
| Results, limitations, literature and updated evaluation priorities | [TEST_RESULTS.md](../benchmarks/2026-10-09-calibration/TEST_RESULTS.md) |
| Permanent logs, reviewed fixture truth, manifests and budget record | [test-evidence](../benchmarks/2026-10-09-calibration/test-evidence/) |
| Current efficiency corrections | [efficiency-corrections.md](efficiency-corrections.md) |
| Active skill and maintenance checks | [SKILL.md](../skill/scientific-workflow/SKILL.md), [maintenance.md](../skill/scientific-workflow/maintenance.md) |
| Native capture/launch and fixture tooling | [native_calibration.py](../scripts/native_calibration.py), [semantic_fixture.py](../scripts/semantic_fixture.py) |

Prepared scratch directories are `/tmp/workflow-test-plan/live-qualification`, `live-baseline` and `live-workflow`. They existed at handoff and are temporary. Permanent manifests are evidence, not a portable runnable copy. Verify frozen source/settings/catalogs before use; changed source invalidates preparations. A safe non-executing pair check is:

```sh
python -B scripts/native_calibration.py check-pair \
  --output /tmp/workflow-test-plan/live-baseline \
  --peer /tmp/workflow-test-plan/live-workflow
```

Codex transcripts live under `~/.codex/sessions/`; Claude transcripts under `~/.claude/projects/`. One inspected Claude workflow session is `~/.claude/projects/-home-hao-githubrepo-scientific-workflow-skill/856948b7-9833-4325-b6e8-778af0ac0c7f.jsonl`. It is a source lead, not a preselected representative sample. Avoid broad transcript exports and raw context dumps.

Both installed skill links point directly into `skill/scientific-workflow/`, so edits there affect live sessions immediately. The skill structure checker needs `/usr/bin/python3` on this host because the default environment lacks YAML support. Use the existing validation commands in maintenance guidance. Required instruction health is `agent-workflow check --repo .`; no native config update is part of this handoff.

Suggested opening request for the next session:

> Read `AGENTS.md` and `docs/STATE.md`. Focus on workflow efficiency and the proposed bounded retrospective. Establish a small sampling/analysis plan from existing evidence before further paid trials. Preserve native Codex/Claude agents, other sessions, the unresolved budget gate and Project2's pause. Use one execution owner and delegate only work it can omit. Complete the scoped checks and local checkpoint.

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
