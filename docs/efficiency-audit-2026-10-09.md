# Codex and Claude execution-efficiency audit - 2026-10-09 UTC

The hierarchies are reasonable starting allocations, but they do not by themselves make execution efficient. The important controls are task ownership, selective review, bounded context and event-driven progress. This maintenance closes specific instruction gaps and adds a deterministic review-packet check. It does not establish that every future issue is eliminated, that lower effort preserves quality, or that money/tokens were saved.

This work is separate from paused Project 2. No scientific implementation, tests, jobs or outputs are authorized here. Native Claude agents/links/settings and Codex profiles/config remain unchanged. The shared skill and its native adapters change; neither runtime is made to emulate the other.

## Current setup checked

| Layer | Codex | Claude Code | Assessment |
| --- | --- | --- | --- |
| Main | gpt-6.1-sol / high | sonnet, Sonnet effort high | Suitable for ambiguous work. The main can execute directly; avoid adding a same-tier worker by default. Main high is not proven optimal for all tasks. |
| Mechanical support | gpt-6-luna / high, reader roles | haiku / high, mechanical explorer | Use only for sizeable bounded work that saves owner effort; direct tools handle tiny lookups. Claude explorer cannot trace logic. |
| Implementation | gpt-6.1-sol / medium | sonnet / medium | Reasonable for bounded delegated implementation; not a compulsory second owner. |
| Difficult analysis | gpt-6.1-sol / high | sonnet / high | Use for a concrete analytical requirement, not slow jobs or status. |
| Consequential review | gpt-6-astra / high | opus / high, no shell | Preserve user policy; selective scoped reviews, complete evidence and concise findings. High reasoning remains potentially costly. |
| Capacity | Current harness advertises 4 total active slots | Installed Agent cap 3, depth 1 | Availability is not a workload target or spend cap. Claude's cap has exceptions and does not cover every mechanism. |
| CLI version inspected | 0.162.0 | 2.1.295 | Configuration/CLI evidence only; no new five-role dispatch campaign. |

Model/effort force variables were absent in the inspected Claude user settings and current shell. The local project settings contain no inspected model/effort/cap override. This does not establish every launch environment, managed provider policy or spawn-hook behavior. Native definitions have no new changes; installed identity comparisons cover them.

## Issues, evidence and fixes

Observed means supported by the prior run/benchmark or inspected configuration. Risk means the old instructions/runtime allowed the behavior; it was not measured as a new occurrence here.

| ID | Issue and evidence status | Change or retained boundary |
| --- | --- | --- |
| 1 | Same-tier coordinator plus execution worker can repeat dependent inspection/debugging. Prior overlapping inspection was observed; compulsory same-tier delegation is a risk. | Main-as-owner is explicit. Delegation needs a useful bounded lane; coordinator integrates rather than repeats. |
| 2 | All reading/writing can be incorrectly routed to Luna or a mechanical explorer. Observed routing concern. | Reasoning/decision ownership controls allocation. Sol/Sonnet owner reads/writes its own files; helpers return ambiguity. |
| 3 | Cheap-model tiny lookups still incur startup, prompts and synthesis. Risk; explorer benefit was not shown in the small benchmark. | Direct tools are the default for known small lookups/checks. Support must save substantial owner work. |
| 4 | Known incomplete packets repeatedly activate expensive review. Observed in paused-run audit. | Readiness/completion first needs named terminal outcomes and exact artifacts. Optional packet helper detects missing or changed evidence before review. |
| 5 | Blanket costly review at every stage or minor code issue. Risk from broad trigger wording. | Review has a blocked consequential decision, scoped requirements and evidence that changes it. Routine debugging/checks stay with the owner. Required user/project reviews are preserved. |
| 6 | Planner/main Opus work followed by duplicate Opus review; same author then certifies completion. Duplication risk; independence is a correctness concern. | Planning assistance and independent review are distinguished. Do not switch main to Opus just to prepare another Opus packet. Fresh completion after plan authorship remains required. |
| 7 | Long reviewer output and high effort can cost much more without added detection. Observed in the frozen small Claude benchmark. | Narrow the question, require one scoped pass and concise actionable findings. Do not route trivial tasks to reviewers. Native effort is retained because another level lacks matched quality evidence. Final brevity cannot cap hidden reasoning. |
| 8 | Run duration/input volume treated as reasoning difficulty and triggers automatic high effort. Old Claude adapter allowed harder OR longer tasks. | High per-call effort now requires a concrete reasoning need. Latency, bulk input and unchanged polling are not escalation reasons. |
| 9 | Frequent waits/polls/messages during one slow operation. Observed. | One progress owner; native notifications first. Otherwise back off unchanged polling according to job duration/safety deadline. Hard limits use deterministic watchdogs. |
| 10 | Coordinator and worker both watch the same job; resuming an idle worker solely for status. Risk. | No parallel watchers, turn-triggering acknowledgements or status-only worker relaunch. User updates do not require another worker turn/read. |
| 11 | Tool timeout mistaken for process termination and creates duplicate expensive jobs. Risk; interrupted execution needs real ownership evidence. | Inspect owned process and terminal receipt before relaunch. Preserve other sessions' jobs. Scientific retry authority does not follow from software recovery. |
| 12 | Repeated full packets/hashes/status, unrelated full-history forks and repeated authority reads. Packet repetition observed; context duplication risk. | One contract/manifest; version deltas and paths. Fresh bounded support/review where native tools support it. Re-read authority at entry/interruption/change, not every unchanged poll. |
| 13 | Large tool output floods context, then gets trimmed only after ingestion. Risk also demonstrated by overly broad documentation retrieval during this audit. | Bound output at the source; return relevant excerpts/counts plus full logs. Retain failure categories/counterevidence. No savings claim from caching repeated context. |
| 14 | Coordinator redoes the reviewer's entire inspection. Observed overlapping inspection. | Coordinator checks requirement coverage, versions and consequential outputs; no duplicate full audit without a concrete unresolved concern. |
| 15 | Delegates read the skill and create their own team/review/plan cycle. Risk, especially through inherited project instructions. | Shared orchestration explicitly applies to the coordinator. A delegate follows its bounded brief/native restrictions; no new orchestration without assigned authority. |
| 16 | Free slots become an agent target; concurrency cap mistaken for spend cap. Risk. Claude docs describe exceptions and separate workflow/team limits. | Useful independent lanes only, reserve review capacity and name conditions for another call. No retries of unchanged capacity failures or sessions to bypass limits. |
| 17 | Model/effort names or agent narratives mistaken for runtime provenance; force variables/provider substitution defeat hierarchy. Risk supported by native docs. | Check relevant setup/exposed dispatch metadata when it changes; disclose mismatch. No repeated model-identity questions or unknown-model substitutions. |
| 18 | All-role smoke calls after every skill edit or repeated full passing suites. Risk from old maintenance wording. | Affected-role metadata/smoke check after actual routing/CLI changes; no five-role ritual for skill-only changes. Focused and project-required broad checks remain. Repeat only affected checks. |
| 19 | Reviewer without shell asked to supply missing terminal checks, pushing expensive synthesis/reconstruction. Risk in Claude. | Owner prepares scoped diff and terminal command-output artifacts first; reviewer does not execute them. |
| 20 | Review/recovery feedback silently authorizes more scientific attempts or clears pause. Correctness and cost risk. | Preserve retry envelopes, scientific gates and persistent pause. Workflow maintenance does not resume Project 2; no fallback or new run from review alone. |
| 21 | Added efficiency prose itself increases recurring context. Observed during staging. | Shorter core/active adapters; conditional coordination details in a separate reference. Measured byte sizes below; no token/cost conversion asserted. |
| 22 | A completeness checker can be confused with scientific readiness or accept fabricated/omitted evidence. Risk introduced by the new helper. | Helper binds declared artifacts/check logs, reports failed/skipped outcomes and leaves `gate_decision=not_evaluated`. It cannot infer omitted requirements or verify scientific truth. |
| 23 | Failure recovery destroys concurrent edits or falsely reports clean rollback. Found and corrected in prior independent installer review. | Existing identity-aware recovery and regression coverage retained; no new installer mutation. General crash/concurrency isolation is not claimed. |
| 24 | Cached input/output/reasoning accounting or small seeded tests support false savings/model rankings. Risk; original benchmark includes truth corrections. | Separate cached/uncached input and output; reasoning is part of output. Preserve frozen evidence and matched-outcome limits. No new price estimate, model ranking or savings percentage. |

These are all issues identified in this scoped audit, not a claim that no other failure mode exists. Routing, output discipline and progress cadence remain instruction-level controls. The packet helper enforces structural completeness only when used; it is not installed as a global hook or runtime scheduler.

## Context-size check

Exact UTF-8 file bytes, compared with checkpoint `158a90a`; not token counts or measured charges:

| Normally loaded guidance | Before (bytes) | After (bytes) |
| --- | --- | --- |
| Shared core | 7708 | 5975 |
| Core plus Codex adapter | 11373 | 9184 |
| Core plus Claude adapter | 10784 | 9410 |

The conditional coordination reference adds detail only for substantial delegation/many-artifact review/slow jobs. Agent discovery descriptions and native frontmatter are unchanged. The additional reference can increase context in those cases; its value must be judged by actual outcomes and avoided coordination, not assumed.

## Validation and limits

Required checks: all existing installer regressions plus packet-check tests, skill structure/local references/native profiles, source-preservation hashes, scoped independent review on a complete packet, actual installation/instruction-health checks and a local checkpoint. Terminal outcomes and independent disposition are recorded in `efficiency-validation-2026-10-09.md` after validation. No expensive headless campaign or scientific test is a maintenance prerequisite.

[OpenAI multi-agent guidance](https://developers.openai.com/api/docs/guides/responses-multi-agent) warns that subagents can increase tokens and fit poorly with dependent work/shared state or a dominant slow operation. [OpenAI subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) describes context/model/effort tradeoffs. [Claude subagent docs](https://code.claude.com/docs/en/sub-agents) describe model/effort precedence, context and concurrency exceptions; [cost guidance](https://code.claude.com/docs/en/costs) supports targeted context/agent use. The preserved `benchmarks/2026-10-08/RESULTS.md` is small-task Claude evidence with original limitations; it does not validate these new rules.

Still unmeasured: new-session native dispatch, actual cost/latency reduction, whether lower effort preserves quality, whether a given extraction/reviewer helps a real long task, and enforcement across every launch mechanism. Do not change pinned native defaults on speculation. A future authorized matched evaluation should compare accepted outcomes, failed attempts, uncached/cached input, output, wall time and independently verified truth with a single-agent baseline; add no large campaign automatically.
