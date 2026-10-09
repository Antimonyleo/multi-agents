# Workflow efficiency corrections

Scope: implement the six issues identified from the original native pilot and coordinator execution. One execution owner, offline validation and one independent completion review. No new benchmark inference, native-agent/model/settings changes, push or scientific execution. Project2 remains USER_PAUSED_DO_NOT_RESUME.

## Changes and limits

| Issue | Implemented correction | Evidence/check |
| --- | --- | --- |
| Coordination added without replacing work | Delegation admission names replaced owner work, bounded return and acceptance check; owner integrates rather than repeats. Required independent challenge is justified separately. | Skill entrypoint and role triggers; independent review of routing |
| Excess context on routine work | Entrypoint reduced from 841 to 429 words; direct-script and single-owner paths finish without role/coordination references unless a project gate requires them. | Word counts and preserved boundary review; actual runtime token reduction unmeasured |
| Workload did not test intended benefit | Inventory and template prose explicitly classified as scriptable extraction/overhead controls. No helper benefit inferred from file count; implementation/review need relevant work and checks. | Existing prose fixture preserved; guidance and pair-check limitations |
| Cheap role/tool mismatch | Reader jobs must fit native tools. Claude Haiku stays Read/Grep/Glob; scriptable processing uses direct tools. A capable execution owner retains dependent implementation. | Native definitions unchanged; role trigger/tool-fit requirement |
| Coordination and accounting overhead | Existing task record is the source of status; no routine parallel readiness/progress/completion narratives. One event-driven progress owner. Distinguish recurring task and one-time setup/evaluation cost; include both for project spend, marking unavailable usage unknown. | Coordination reference; manifest cost scope; no additional model-backed benchmark runs in this correction |
| Validation missed experimental confounds | Matched routing mode exposes equal tools/skill snapshots. Separate deployment mode declares capability differences. Paired launch guard compares actual commands, inputs, schema, models/settings/agents, source and budgets. | New regression reproduced the old unequal-tools failure, then passed; drift, legacy, missing-peer and missing-telemetry tests |

## Correction to the original pilot interpretation

The original Claude baseline omitted Agent/Skill while the workflow enabled them. Startup events also report 73 skills and 7 plugins in the baseline versus 72 skills and 6 plugins in the workflow. Their presence/counts are observed; their individual cost contributions are unknown. Its observed cost increase is not an isolated instruction effect. Enabling capabilities can have a real deployment cost; matching capabilities for another question does not remove that cost from overall deployment accounting. Preserve the frozen raw runs and original version-bound review; this correction supersedes any matched-tools interpretation.

Read-only replay of the original traces yields four distinct assistant message IDs per arm. Baseline: first input context 8,011 tokens, total input processed including cached content 41,842, CLI list-price estimate $0.2307956. Workflow: 20,151, 96,488 and $0.347201. No delegates ran. Astra's completion review and coordinator/setup activity were outside those arm estimates, so they cannot explain their difference and complete project spend remains unknown.

The updated normalizer deduplicates assistant-message usage and tool-call fragments by stable identities. Mixed complete and incomplete response telemetry leaves aggregate totals unknown; later fragments can complete the same identified response. Observed response IDs are not server request counts. No parent/child totals are silently added and no automatic savings verdict is issued.

## Validation and checkpoint

Final offline validation: 61 repository tests passed, including 23 capture/pair-control tests. The structure validator passed (7 local links, 5 Codex profiles, 74 protected historical/native sources), the skill checker passed, both-runtime installation checks passed for 12 destinations, instruction health passed and git diff whitespace checks passed. Independent review found three harness defects: identical command tampering could evade between-arm checks, new local capabilities escaped recorded-path checks, and mixed telemetry could appear complete. Focused regressions reproduced all three. Corrections bind each command to declared controls and its checked workspace, re-enumerate all user agent files and shared/runtime skill entrypoints, and mark incomplete response totals unknown. All focused regressions and the final suite pass. Targeted independent followup: accepted all three corrections; no remaining finding in scope. Test output is retained at `/tmp/workflow-efficiency-fixes/required-tests.log`. Model-backed savings remain unmeasured. Instructions cannot enforce zero wasted reasoning or remove a native runtime's always-loaded tool catalog. The existing exact-cwd Codex child collector limitation remains: validate broader child discovery, tool restrictions and accounting before a delegated-cost claim.

The adapter now requires a peer preparation for live execution. Legacy prepared commands need a newly authorized/reprepared pair; existing execution records remain frozen. A passing preflight establishes declared controls, not inference authority, identical runtime caching, a hard Codex monetary cap or scientific acceptance. A peer's failed/incomplete capture blocks automatic continuation of that comparison.

Further live evaluation requires a representative question and bounded scope/budget. Do not launch another panel merely to obtain delegation or a favorable cost result.

Local capability fingerprints cover user agent files and skill entrypoints, including additions/deletions. They exclude plugin contents, built-in capabilities, remote catalogs and transitive skill resources. Before attributing costs causally, separately validate the effective runtime catalogs from startup evidence or runtime-specific controls; a matching local preflight alone cannot establish that claim.
