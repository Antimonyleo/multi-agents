# Native extraction calibration adapter

Current entrypoint: `scripts/native_calibration.py`. Prepare two isolated arms before running either:

```sh
python scripts/native_calibration.py prepare --provider claude --comparison routing --arm baseline --output /tmp/calibration-baseline
python scripts/native_calibration.py prepare --provider claude --comparison routing --arm workflow --output /tmp/calibration-workflow
python scripts/native_calibration.py check-pair --output /tmp/calibration-baseline --peer /tmp/calibration-workflow
```

Preparation and pair checking make no model calls. `run --output ARM_DIR --peer OTHER_DIR` requires separately authorized inference, a passing pair check and frozen versions. It refuses an existing local trace or a peer that started without successful terminal completion. The existing finite timeout/process-group runner remains the executor; this is not a new orchestrator or a hard overall spending scheduler.

`routing` matches tools and local skill availability, varying explicit workflow use and optional delegation. `deployment` intentionally varies local skill availability and Claude Agent/Skill tools. The latter measures those deployment differences, not an isolated instruction effect. Global catalogs can remain loaded in both modes; neither mode models an entirely uninstalled runtime. Match native model/effort, settings and user agent/skill-entrypoint inventories, source, task/schema/truth, declared budgets, permissions and effective command controls. Each launch command must also equal the canonical command built from its own declared controls and checked workspace. Local inventories detect additions and changes; they do not cover plugin contents, built-ins, remote catalogs or transitive skill resources. Separately validate effective runtime capabilities before causal attribution. Actual runtime context/cache variation still needs measurement.

Both the 96-file inventory and the existing 40-file prose fixture remain available (`--task inventory|prose`). Both have deterministic reference extraction. They are correctness/overhead controls; file count or prose packaging does not establish useful delegation, implementation quality or review benefit. See the [maintenance evaluation guidance](../../skill/scientific-workflow/maintenance.md#efficiency-evaluation) before choosing another workload or claim.

The collector preserves native evidence and provider totals. Latest usage per stable Claude assistant-message ID supplies response/context observations without counting repeated fragments twice. Mixed missing identities or usage leave aggregate totals unknown; a later fragment can complete an identified response. These are not server request counts. Child/cumulative accounting remains conservative: missing data is unknown, parent and child totals are not automatically added, and no automatic net-savings verdict is issued. Recurring task versus one-time setup/coordinator/review scope must be reported explicitly.

Codex candidate transcript collection currently uses the exact workspace cwd, so a child that changes cwd may be missed. Validate live child discovery, restrictions and usage inclusion before delegated-cost claims. The timeout runner's process-group cleanup does not prove arbitrary external children stopped. Native permissions and tools differ across providers; compare within a runtime.

The four original pilot runs and `pilot-evidence/used_adapter.py` remain frozen. Legacy preparations cannot pass the new matched-pair check; retain their original execution records instead of silently replaying them through a changed adapter. The original Claude pair had unequal tools and different startup skill/plugin catalogs and cannot isolate workflow instructions. Costs observed there remain valid deployment observations subject to its stated cache/order limits.

The wrapper depends on the existing host harness recorded in each manifest. No global agents/settings are rewritten. Offline tests make no model calls. Project2 remains paused.

## Next test plan: reliability before efficiency

Status: execution authorized by the user; offline stage A accepted. Native stages remain pending the budget constraint. See [execution results](TEST_RESULTS.md). Independent plan review accepted the design and limits on 2026-10-09. Based on the independent audit of `dfe47fd`; source is now `5ee26a0`, which restores scientific-evidence guidance. Preserve that later change. This plan supersedes the unlaunched prose pilot, not historical evidence. The user authorized executing this plan. Its gates, limits and conditional allocations still apply. Project2 stays paused. Native agents/settings and frozen benchmark records stay unchanged.

### Questions and order

1. Can the harness detect invalid runs and terminate its owned processes?
2. Does the native runtime expose enough reliable evidence to evaluate one parent/helper task?
3. Does a useful, bounded helper actually replace owner work and improve accepted completion?
4. Does the workflow select the right action without being told the answer?

Answer these separately. Forced delegation measures an allocation, not autonomous routing. A correct answer with invalid accounting is a quality observation, not a cost result. Do not build a new orchestration framework or expand the extraction/model matrix.

### A. Offline reliability gate

One capable execution owner fixes the dependent harness chain, using the existing reproduced failures. Use temporary fixtures and fake runners; no model starts. Preserve small reproductions in regression tests rather than relying on `/tmp` audit logs indefinitely.

| Test family | Cases | Required result |
| --- | --- | --- |
| Owned-process cleanup | Normal completion; timeout with parent alive; parent exits on TERM while child ignores TERM; child remains after normal parent exit | Bounded TERM/KILL cleanup for verified owned process group. Receipt distinguishes terminated, absent and unresolved; unresolved blocks continuation. A separate unrelated sentinel survives. Reap owned children where possible; never infer cleanup solely from parent exit. |
| Provider telemetry | Empty/missing usage; wrong types, bools, negative counts; partial messages; duplicate fragments; valid zero counts | Provider-specific schema validates usable totals. Unknown stays unknown. Failures block the next arm. Final usable provider totals and message-level completeness are separate fields; neither silently substitutes for the other. |
| Delegation boundary | Permitted explorer; reviewer/worker; missing identity; baseline delegation; repeated fragments; multiple distinct helpers; attempted nested child | Allowed role, unique starts and depth verified from available native evidence. Unauthorized or unresolved identity cannot pass. Tool-call and native-child counts reconcile without double counting. |
| Child discovery | Descendants at same/different cwd; unrelated thread at either cwd; duplicate traces; missing child transcript; malformed/string source fields | Follow verified parent IDs across cwd, include only descendants, exclude unrelated sessions. Missing descendants invalidate family accounting; no broad export of other sessions. |
| Pair controls and continuation | Existing command/input/catalog drift regressions; incomplete/failed peer; missing metrics; telemetry/boundary/cleanup failure; attempted retry | Every required failed/unknown check blocks before importing/starting the runner. Existing canonical-command and capability tests stay passing. |
| Scoring and records | Wrong/omitted/unsupported findings; clean negative controls; trace parsing failure; missing receipt | Incorrect outputs fail quality; incomplete execution is recorded as incomplete. Reference answer and grader agree independently before any inference. |

Acceptance: reproduce each confirmed defect on the old behavior, pass focused regressions after correction, then run the named repository suite and structure/skill/install/instruction checks once. The shared external runner is a separate repository: inspect its authority and working tree before modifying it, test its affected behavior in an isolated copy, and preserve active science and other sessions. Do not run a scientific project's broad suite in its canonical tree. Use the existing independent harness auditor for one correction review when evidence is ready, then checkpoint.

### B. Prepare one informative fixture and qualify capture

Prepare offline before spending. Choose one runtime first; Claude is the provisional choice because the previous Codex arm had a startup failure and Claude exposed a reported session price. This is operational convenience, not a provider/model ranking. Freeze actual runtime/version, native model/effort, local and effective capabilities, prompts, skill source, fixture, scorer, budgets and permissions. A source change invalidates the prepared pair.

Use a frozen inactive corpus: a configuration option flowing through CLI parsing, validation, defaults and consumers across approximately 8–12 relevant modules. Include precedence, invalid-input and boundary cases plus irrelevant files. Ask for behavior and source-backed mismatches. Give the helper a coherent independent subset; its return must be shorter and cheaper to integrate than rereading the subset. The native reader must be able to finish using its existing tools. File count alone is not evidence of useful work.

Verify the answer key against executable behavior where possible and an independent inspection of the fixture. Keep answer keys and hidden checks outside model-accessible workspaces. Validate true defects and clean controls before calls; exclude disputed truth before freezing, not after seeing results. Use deterministic scoring for structured claims/citations and inspect only ambiguous cases, blind to the arm where practical. Record any grading change and invalidate affected comparisons rather than silently rescoring to favor an arm.

After A passes, one harmless qualification session may call one allowed native helper. This is an explicitly labeled capture smoke test, not an efficiency arm. Implement a narrow qualification path with the same boundary/capture/cleanup checks; do not bypass paired-run controls using a dummy peer. Verify observed role/model, allowed and denied scratch-only operations, parent/child relationships, effective startup catalogs, accounting inclusion and cleanup. Use native evidence rather than asking a model to state its identity. Test dangerous timeout shapes offline, not through paid calls. Missing live enforcement evidence remains unknown and blocks the corresponding claim.

Gate: all owned tasks terminated; output and boundaries pass; parent/child usage inclusion is established without double counting. If this cannot be established, stop with an operational result. No cost comparison follows an unresolved qualification.

### C. First benefit comparison

Run one matched pair on the prepared fixture:

- Baseline: same capable main, direct tools, no helper.
- Treatment: same capable main, exactly one bounded native reader assigned the independent subset. Owner omits that investigation and integrates its evidence.

Both arms receive identical capabilities, base task, checks, budget and coordination guidance except the allocation instruction. Neither gets hidden answers. Preserve required reviews equally; no added per-arm reviewer for this diagnostic task. The coordinator does not solve the task alongside either arm. Grade the final artifact and traces after terminal completion.

Measure quality first: all required behaviors and boundary cases correct, citations valid, no fabricated findings or authority violations. Also record owner rereads of the delegated subset and whether each has a concrete discrepancy/required audit justification. Tool traces are an observable proxy; they cannot reveal all internal duplicate reasoning.

Then report elapsed time through integration and validation, new/cached input and output, parent/helper usage, failed attempts, retries, and required supervision/review. Retain raw native evidence and distinguish provider price estimates from actual billing. Separate one-time preparation/evaluation from recurring task cost; include both only when reporting total project spend. Unknown coordinator/child usage prevents a complete-cost savings claim. Raw tokens across different models/providers are not an interchangeable cost metric.

Pre-register the practical decision: no quality or boundary regression; a candidate benefit is at least 15% less measured recurring cost without more than 10% extra elapsed time, or at least 15% less elapsed time without more than 10% extra measured cost. These are proposed engineering thresholds, not measured effects or statistical significance. If full cost is unavailable, report the narrower measured scope without declaring this criterion met. Smaller or conflicting differences are inconclusive. A failed-quality arm cannot win by being cheap.

Randomize which arm runs first and record cache state. Use fresh sessions; equal capabilities and fresh sessions do not guarantee equal caching. Preserve failed starts in the operational denominator. A confounded or missing arm yields an incomplete comparison, not a replacement run.

### Budget, stopping and repetition

The current state records a $2 target and $3 ceiling for a pilot. Before launch bind that budget to an explicit accounting scope; do not silently reinterpret it as a per-session allowance or claim it covers unmeasured coordinator/review cost. Proposed benchmark allocation: at most $0.40 for qualification and $0.80 per comparison arm, including their children, reaching the $2 target. These are spending caps, not expected prices or promises that tasks will finish. The remaining $1 is reserve, not authority for retries or another pair. If native limits cannot bound the required parent/child scope, establish an enforceable narrower allocation before starting; do not call a timeout a hard dollar cap.

Initial ceiling: three parent starts and two helper starts total; one active parent at a time; each parent family has a 300-second deadline plus a bounded cleanup grace. All failures consume starts and budget. Stop on invalid capture, unexpected role/depth/tools, unresolved cleanup, changed authority, budget/deadline exhaustion or scope violation. Recovery records evidence; it does not automatically relaunch. No reviewer runs inside this pilot allocation.

A reverse-order pair is conditional future work with its own remaining/renewed budget, identical per-arm limits and a predeclared reason. Consider it only after a valid first pair to check whether a promising or decision-relevant result persists; record both pairs regardless of outcome. Do not keep adding runs until a favorable answer appears. Two pairs remain diagnostic. Default changes need a broader held-out workload set and uncertainty assessment designed from observed variation.

### D. Behavioral and later workload coverage

After reliable capture, test these separately when their decision is needed. Prepare offline expectations now; live runs are outside the initial three-parent envelope.

| Question | Smallest useful test | Acceptance / limitation |
| --- | --- | --- |
| Routine restraint | Explicit-rule extraction with an anomaly, workflow chooses actions | Correct complete result, no helper/reviewer, no unnecessary coordination record. Tests behavior, not helper economics. |
| Autonomous helper selection | New held-out corpus with useful independent lane, helper optional | Justified choice and accepted result; if no helper runs, record non-delegation, not failed proof of helper benefit. Compare whole-task outcomes. |
| Review cadence and pause | Controlled staged decision: consequential exception, unchanged evidence, explicit pause | One justified review, unchanged disposition reused, no resumed action while paused. Use deterministic replay first; one live sequence only if adherence is the unresolved question. |
| Dependent execution ownership | Multi-module repair with hidden behavioral tests in a disposable fixture | One capable owner completes checks; quantify supervisor repetition/integration. Main-versus-worker is a separate allocation comparison. |
| Consequential review value | Verified defect-bearing decision packets and clean controls | Score prevented wrong decisions, missed defects and false positives. Keep mandatory gates equal; never remove a required review to manufacture savings. |
| Second runtime | Repeat only affected capture and behavioral checks | Native tool/permission differences require their own evidence. Do not infer Codex behavior from Claude or repeat a full model matrix. |

Use one execution owner and native completion notifications throughout; no status-only subagents or per-task Astra reviews. Reuse existing audit findings. An independent reviewer checks the corrected reliability gate and the final decision supported by completed benchmark evidence; intermediate passing tests do not create new review milestones.

### Completion and next action

The planning checkpoint is complete when test families, scoring, boundaries, budgets and conditional stages are recorded and independently challenged. Execution is complete stage by stage only on its stated acceptance evidence; an invalid/failed pilot is a completed observation, not proof of efficiency. Keep this section as the plan and link results from `docs/STATE.md`; do not create parallel status narratives. Stage A is complete within its reviewed scope. The next action is resolving the live budget constraint, then native qualification; a passing offline gate alone does not lift another gate or the scientific pause.
