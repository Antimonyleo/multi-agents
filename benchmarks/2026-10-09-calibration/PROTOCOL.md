# Bridging workflow policy to measured execution - 2026-10-09

Status: FOUR PLANNED PILOT STARTS EXECUTED; ONE OPERATIONAL STARTUP FAILURE. See [results](RESULTS.md) and `pilot-evidence/SUMMARY.json`. The preparation checkpoint sections below describe the pre-launch state; this execution checkpoint does not claim that all efficiency questions are resolved.

## Objective and boundaries

Check whether the shared workflow selects capable roles at useful moments and reduces whole-task time/cost without reducing required quality, scope preservation or evidence. Compare within Codex and within Claude; do not rank providers using unequal token formats or prices. Preserve existing native agents/models/effort/tools/settings. No Project2 implementation, tests, jobs, construction, prediction, acquisition or MD; its pause remains in force. No push, configuration changes, unbounded model campaign or automatic retries.

The user's three concerns map to observable outcomes:

| Concern | Evidence that can answer it |
| --- | --- |
| Easy work belongs on smaller models only when delegation helps | Exact result quality plus whole-run parent/child usage and elapsed time, compared with main/direct-tool handling |
| Demanding work gets a capable execution owner | Named checks and accepted artifact, one owner, escalation evidence and actual configured/observed role information |
| Strong review occurs at project planning/major phases | Native trace with the blocked decision, declared milestone, complete evidence and reviewer calls; no calls on routine tasks/status |

## Reuse and known harness gaps

Reuse `/home/hao/githubrepo/sequence_design/tools/workflow_evaluation/run.py` for offline preparation, artifact grading, pause/resume/read-only controls and finite timeout behavior. Its 13 deterministic tests passed. Six isolated routine/resume/paused fixtures were prepared for Codex and Claude with no inference; see PREPARATION.json.

This harness disables user configuration/customization and does not prove native `scientific_*` discovery, inherited role restrictions or aggregate child usage. Its Claude isolated mode cannot invoke the shared skill. Do not call those cases native workflow success or adapt a comparison merely by changing the requested main model. The frozen older Claude benchmark remains unchanged and is useful only as prior limited evidence.

Before live native comparison, add the smallest native capture adapter to the existing harness or a narrow wrapper; do not build a second general orchestrator. Preserve authentication in its existing location and export no credentials. Use isolated scratch workspaces with exact copied guidance and native role definitions/settings needed for the test, recording every deliberate difference from installed behavior. Match permissions/tools across arms within each runtime; do not claim cross-runtime isolation equivalence.

Required adapter outputs: exact source/prompt/fixture identities, parent-child call relationships, role names, requested versus observed model/effort where exposed, commands and results, preserved/changed files, final artifact, termination/timeout receipt and native usage. Validate capture with stored/synthetic traces before live use. If child usage, model identity or cleanup cannot be verified, mark that field unverified; do not repeatedly launch models merely to fill metadata.

## First native pilot: four top-level runs

Choose one substantial, bounded extraction workload with deterministic exact-output truth from a frozen fixture. It must represent actual support work rather than artificially force a helper for one trivial lookup. Include direct scripts/tools as permitted solutions. If a script solves it most efficiently, non-delegation is a valid outcome.

| Runtime | Baseline arm | Workflow arm |
| --- | --- | --- |
| Codex | One main owner using the same main model/effort, tools, fixture and checks; no optional delegate | Same owner settings with current shared workflow; zero or one bounded Luna support call if justified |
| Claude | One main owner using the same main model/effort, tools, fixture and checks; no optional delegate | Same owner settings with current shared workflow; zero or one bounded Haiku support call if justified |

One paired task per runtime gives four top-level starts and at most two optional support starts. No routine expensive reviewer or five-role smoke ritual. This is a diagnostic pilot, not enough evidence for a universal default or significance claim. A workflow arm making no helper call can show efficient non-delegation but cannot establish small-helper benefit.

Keep the base task wording, artifact checks, compute/tools and initial context the same except the workflow/delegation intervention. Freeze prompts, versions, scorer and exclusions before calls. Counterbalance arm order (baseline-first in one runtime, workflow-first in the other); for later repeats use within-runtime alternation/randomization rather than treating provider difference as an order correction. Record environment/caching differences. All arms retain the same scientific/scope boundaries.

Ground truth must be checked independently before inference, using raw fixtures and accepted/rejected scorer controls, not the intended model response. Reuse independently exercised reference checks where appropriate. Register corrections and restart only the affected comparison; never rewrite a scorer after seeing results and silently keep the old score.

## Measure the whole task

Capture from task start through accepted artifact and named checks, including owner integration, delegate prompts/returns, failed attempts, required review and supervision. Do not compare a helper's isolated call against the main owner's entire task. Record:

- Outcome/check completion, omissions, incorrect claims, unauthorized writes/runs and preserved boundaries.
- Parent/child requested and observed role/model/effort, with explicit unknowns.
- Cached input, uncached input, cache-creation input where provided, output and reasoning separately. Reasoning is part of output; provider field meanings differ.
- Calls/turns, status-only activations, waits/polls, repeated reads/packets, unexpected expensive review and duplicate execution ownership from recorded traces. No extra model watchdog is used to collect these.
- Whole-task wall time, startup/tool/queue time when exposed, termination and retries.
- Provider-reported cost or a dated price-based estimate only when complete and interpretable. Token totals are not invoices; missing child usage is unknown, not zero.

Validate whether parent totals already include children before aggregation. Deduplicate by stable request/event identifiers; do not sum cumulative snapshots as if incremental. Preserve raw per-provider fields alongside any normalized view. If aggregation semantics are unresolved, do not publish a net-cost claim. A short final answer cannot prove low reasoning cost.

## Budgets, stop conditions and readiness

Before launch, record a total model-call budget/resource envelope across parents and children, a finite wall deadline, permitted tools/paths and termination method. The pilot start cap is four top-level sessions plus at most two optional support calls. Do not turn this cap into a target. Monetary enforcement is not assumed: if one runtime lacks a complete enforceable USD limit, state that and use a supported declared limit rather than advertise a hard USD cap.

Native adapter readiness, independently checked truth and live-run budget/scope are prerequisites; they are not yet complete at this preparation checkpoint. A timed-out CLI is not proof all owned children stopped. Cleanup must target this test's owned session/processes, never shared daemons or another session's agents. No automatic extra sessions or scientific retries to recover an operational failure.

Stop the affected lane on violated scope/pause, uncontrolled child activity, missing required telemetry, unresolved cleanup or exhausted budget. Preserve the failure receipt. Startup/network failure is operational evidence, not model-quality failure. A fix may justify one separately bounded affected rerun; do not retry unchanged failure.

## Decide from evidence, then expand only where needed

A candidate allocation must meet all quality/boundary checks. If it improves net time or cost, report the other metric and any regression rather than hiding the tradeoff. A cheaper call with more integration work is not a demonstrated saving. One pair is descriptive; close/noisy results remain inconclusive. Predeclare a practically useful improvement and tolerated tradeoff before a default-setting decision; do not invent a confidence score.

After the first pilot, run only the case needed to resolve an actual remaining gap:

| Remaining gap | Next bounded comparison |
| --- | --- |
| Helper break-even point unclear | Another workload size or repeated pair, preserving exact truth and budget |
| Implementation ownership/escalation unclear | One dependent repair fixture with real hidden/reference checks; main alone versus one bounded worker lane |
| Review benefit/timing unclear | One declared major-phase evidence packet with independently verified consequential defects; required reviews stay equal across arms |
| Polling/status overhead unclear | One synthetic slow job with deterministic duration/receipt; verify one progress owner and no status-only delegate/reviewer turns |
| Pause/resume behavior unclear | Existing prepared boundary fixtures, respecting their synthetic pause and frozen receipt |

Never remove a project-required independent review to make a baseline cheaper. Routine-task comparisons have no artificial review requirement; review-benefit comparisons must explicitly preserve any required gate in every arm. Compare optional review strategies only where the task permits that choice.

Repeated observations are needed before changing routing defaults. Keep a conditional rule tied to workload/tools/quality rather than a universal rule that every easy job delegates. Independent major-phase review assesses the completed evidence and proposed policy change once; no reviewer at every trial, poll or minor fix.

## Historical preparation checkpoint and next exact action

Completed: existing harness inspection, 13/13 deterministic tests, six prepared fixtures, source identities/commands and this protocol. Zero model calls and zero scientific execution. Native dispatch, aggregation, task benefit and actual savings remain untested.

Next exact action at preparation (now superseded by RESULTS.md): implement/validate the narrow native capture adapter and freeze the first task's truth/scorer. Then complete the total live-run budget and launch-readiness packet before the four-run pilot. Do not launch inference from the legacy PREPARATION.json commands as proof of native hierarchy behavior. Record pilot results before changing any role/model/effort default.

Basis: [OpenAI skill-evaluation guidance](https://developers.openai.com/blog/eval-skills) recommends captured traces/artifacts with outcome, process and efficiency checks. The two local harnesses supply existing code/evidence patterns; neither proves this new pilot has run.

## Runtime refresh during preparation

A final historical-identity check found the Claude user settings changed outside this task: the current main model is `opus` with configured high effort, rather than the previously inspected Sonnet main. This task did not change or revert that file. All other recorded native agent/config/link identities match the prior audit. `RUNTIME_REFRESH.json` records the observed setting hash; active adapter wording now uses inspected current settings rather than claiming a permanent Sonnet main.

The prepare-only legacy Claude manifests request Sonnet explicitly and disable customization, so they remain synthetic boundary controls, not tests of the installed Opus-main setup. Native pilot arms must freeze the same current main setting, or register Sonnet-main versus Opus-main as a separate controlled intervention. Do not confuse savings from changing the main model with benefits from delegation. This is a material calibration concern, not authority to rewrite another session's chosen default.
