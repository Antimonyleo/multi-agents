# Maintenance for the scientific-workflow skill

## Where things live

| Item | Location |
| --- | --- |
| Agent definitions | Claude: unchanged `agents/scientific_*.md`, linked into `~/.claude/agents/`; Codex: `agents/codex/*.toml`, installed copies in `~/.codex/agents/` |
| Native main/role settings and spawn caps | `~/.claude/settings.json` (`env`, `modelSettings`) |
| Routing rules (this skill) | `skill/scientific-workflow/` in the source repo, linked as `~/.claude/skills/scientific-workflow` and `~/.agents/skills/scientific-workflow` |
| Source repo | `~/githubrepo/scientific-workflow-skill` (edit here; `scripts/install.sh --check` verifies the links) |
| Benchmarks | `benchmarks/2026-10-08/` in the source repo (protocols, `bench.py`, data, `RESULTS.md`) |
| Project review gates | each project's guidance, for example `docs/agent_guidance/delegation.md` |
| Runtime adapters | `references/codex.md` and `references/claude-code.md`; read only the active adapter. |

## Validate a change

Run `python scripts/validate.py` and `python -m unittest discover -s tests -v` from the repository root. These check structure, local references, native profile parsing, protected historical/Claude identities and installer behavior in temporary homes. They do not establish live model routing, scientific success or token savings.

Use an isolated staging copy because edits here are immediately visible through live skill links. Obtain user authority for workflow changes; an explicit request to implement the proposed change is authority for that scoped work, without repeated routine approval. It does not authorize unrelated native-agent edits or new scientific work. Archive conflicting prior sources and keep consolidation and routing improvements in separate commits.

After activation, check `scripts/install.sh --target both --check` and project instruction health with `agent-workflow check --repo PATH` where available. Use a new session for changed profiles. Run fresh model-backed evaluation only when its scope and cost are authorized; use exact versions, objective outcomes, independent truth and a matched budget. Record native traces, permission policy, uncached/cached input, output, latency and price basis separately. Do not run a full expensive benchmark as an automatic maintenance check.

## Efficiency evaluation

Choose the question before preparing trials. `scripts/native_calibration.py prepare --comparison routing` is the default: both arms receive the same tools and local skill catalog, while the baseline declines workflow use/delegation. `--comparison deployment` deliberately varies local skill and supported tool availability; its cost is deployment overhead, not an isolated instruction effect. Installed global catalogs can remain visible in both arms. Preserve user/native settings and label the scope actually measured.

Prepare both arms with the same task, runtime, budget and source version. Run `check-pair --output BASELINE_DIR --peer WORKFLOW_DIR`. `run --output ARM_DIR --peer OTHER_DIR` requires that pair and verifies frozen inputs, launch controls and terminal peer state before importing the runner. These are non-executing validity checks, not inference authority. Legacy preparations remain historical and cannot certify a new matched comparison. A matched manifest does not guarantee identical runtime context or caching.

Inventory and the existing template-based prose fixture are scriptable extraction controls. Use them for correctness, context and non-delegation overhead, not as proof of implementation/review benefit or helper savings by file count. A helper-benefit task must have an independent lane that removes owner work and a return/check cheaper than repeating it. Implementation and major-phase review need their own representative fixtures; preserve required gates in both arms. Do not launch another panel merely because a prior task produced no delegation.

Review the experimental design against the original question before costly runs: workload relevance, changed versus held-fixed variables, command-level tools/permissions, exact truth, caching/order, cost scope and limits. Hashes and passing tests alone do not answer these questions. Count parent, child, integration, failed attempts and required review in recurring task cost. Record one-time setup/evaluation separately and include it for total project spend. Unavailable usage prevents complete-cost claims; a single pair stays descriptive. Use existing traces/offline checks first and the current task record for evidence; avoid another reporting framework.

## Review packet check

For a consequential handoff with many artifacts/checks, reuse the project's packet checker if it has one. Otherwise use `python scripts/review_packet.py /path/to/packet.json` from this repository. The helper is optional for small or self-contained reviews; it does not create another task framework or replace project authority.

The JSON packet names `phase` (`plan`, `blocking`, `readiness`, `completion`), `question`, `scope`, `stop_boundary`, `artifacts` (paths and SHA-256), `required_checks`, and `checks` (unique names, status and terminal evidence paths). Paths are relative to the packet file unless absolute. Plan checks may be `planned`; readiness/completion need terminal evidence for every named required check. Failed checks are terminal evidence, not acceptance. A skipped check needs a reason. A blocking review may acknowledge pending evidence by check name in `acknowledged_missing`; its narrow result cannot certify readiness. All phases require existing, exact artifact versions; avoid shipping this phase schema for every trivial task.

The helper reads files and returns missing/mismatched items plus `packet_complete_for_phase`. It neither launches review nor authorizes execution nor establishes scientific acceptance. It does not infer omitted requirements, decide whether a skipped/failed check satisfies a gate, or verify the correctness of check results. Run it once when assembling/changing the packet, not at every progress poll.

## Check after an agent change or Claude Code update

Use available native transcript/task metadata first. A skill-only edit does not require model-backed calls for unchanged agents. After an actual agent/CLI routing change, verify the affected role with one bounded scratch task and a main model different from the role's model; expand to other roles only if the evidence suggests shared routing failure. The example below is a dispatch smoke check, not a routine five-role maintenance checklist:

    claude -p "Call the one affected scientific role once. Task: Reply with the single word OK. Use no tools." \
      --model sonnet --output-format stream-json --verbose --allowedTools "Agent" --permission-mode dontAsk

The stream shows only the main thread. Read the sub-agent models from the transcripts: `~/.claude/projects/<session dir>/<session id>/subagents/agent-*.jsonl` (`message.model`, `"effort"`), and the role from the matching `.meta.json` (`agentType`). A role that runs on the main model instead of its own is the failure in anthropics/claude-code#100082.

Cost and usage: `/usage` attributes plan usage to sub-agents and skills. `/skill-doctor` shows a skill's context cost and use. For A/B tests of a skill, use the skill-creator plugin evals.

## Evidence basis (2026-10-08)

Claude Code docs: sub-agents, costs, best-practices, model-config. Platform docs: effort, prompting guides for Opus 5, Sonnet 5.5, Haiku 5.5. Anthropic engineering: multi-agent research system. Third-party and issue-tracker reports were used only as leads. Nothing was tested on a real scientific task yet.

## Evolution log

- 2026-10-08: Created. Tiers: explorer haiku/high (mechanical only), researcher and worker sonnet/medium, analyst sonnet/high, reviewer opus/high (fable only on request). Main thread Sonnet 5.5 high. Caps: depth 1, concurrency 3 (guess).
  - Effort basis: Sonnet 5.5 docs say start at medium for well-specified agentic tasks and high for harder or longer ones. Haiku 5.5 docs say medium is the default and low skips checks. Medium models may stop early, so worker and researcher files carry the documented "keep working" rule.
  - Model check (v2.1.294): researcher, worker and analyst ran claude-sonnet-5-5, also under an Opus main thread. After the 2026-10-08 edits, explorer ran claude-haiku-5-5 at high and reviewer ran claude-opus-5-5 at high, both under a Sonnet main thread. Before the edit the reviewer ran claude-fable-5-1, so `model: fable` also works on this account. Effort recorded matched the files.
  - Smoke test of the skill with three scenarios (mechanical count, long-run gate, "use fable"): routing matched the rules. It exposed one gap: it said it would launch the campaign after review. Added the rule that a review does not authorize new execution.

- 2026-10-08: Benchmarked (38 headless runs, about $13). See `benchmarks/2026-10-08/RESULTS.md`.
  Idle cost about +3 to 6% on a trivial task. Skill invoked: +5 to 8%. No delegation in 14
  workflow runs that did not name the reviewer. Reviewer routed by the user: median $0.85
  extra (R/B cost 4.98), no extra detection on one seeded change set. No saving and no
  on-track advantage shown; long tasks untested. No file in the workflow was changed
  because of the benchmark.

- 2026-10-08: Phase 4 compared with Opus alone (12 runs). Workflow (Sonnet main) cost 0.50 to
  0.58 of Opus alone on small tasks with equal correctness; plain Sonnet gives the same saving.
  Review routed to the reviewer cost 2.28 times Opus alone. Nothing in the workflow was changed.

- 2026-10-08: Moved to its own repo, `~/githubrepo/scientific-workflow-skill`. The live paths under
  `~/.claude` are links to the repo, so there is one copy. The benchmark folder moved out of the skill
  directory into `benchmarks/`. No content changed. Model check after the move (v2.1.294): all five agents
  and the skill load through the links; explorer haiku/high, researcher sonnet/medium, worker sonnet/medium,
  analyst sonnet/high, reviewer opus/high.

- 2026-10-09: Consolidated the shared entrypoint and added separate Codex and Claude references. Copied Codex native profiles into `agents/codex/`; Claude native agents, links and settings are preserved. Archived the old Codex skill and home manual for provenance. Added transactional installation, conflict preflight, receipts and rollback. Existing benchmark artifacts remain unchanged. See repository-root `docs/consolidation.md` for activation and verification.

- 2026-10-09: Added coordination rules from the paused-run process audit: one dependent execution owner, reviewer packets ready for the requested decision, changes instead of repeated packets, durable progress during slow jobs and no duplicate full coordinator review. Required evidence/checks and project boundaries stay intact. No token-saving percentage is claimed.

- 2026-10-09: Audited both installed hierarchies and coordination paths. Kept native Claude agents/settings and Codex profiles/config unchanged. Clarified main-as-owner, coordinator-only orchestration, decision-focused costly review, one progress owner with backoff, bounded context/output, effort escalation based on reasoning rather than run length, native override/limit caveats and affected-role-only smoke checks. Added an optional deterministic review-packet completeness check. See repository-root `docs/efficiency-audit-2026-10-09.md` for the issue inventory and measured limits.

- 2026-10-09: Clarified explicit entry/handoff/stop triggers for each role and review scheduling at project scope/planning, declared major phases and final project review. Routine subtasks, time and unchanged status do not trigger review. Required gates and material exceptions remain. Native profiles/config/settings are unchanged. This small instruction refinement needs no extra reviewer dispatch or repeated passing code suite.

## Open questions

- Can the reviewer run at medium effort (the Opus 5.5 default) and still find what high finds? Its cost was 3 to 5 times a whole small task.
- Does the workflow help on a long task (tens of turns, large context)? Not tested; the benchmark tasks were all under $0.40.
- Does `scientific_explorer` ever pay? It was never invoked in 38 runs.
- Is medium enough for worker and researcher on real tasks? Run a sweep on two or three real tasks.
- Does Haiku/high do mechanical lookups without errors? Spot-check the first few results against the files.
- Does the concurrency cap or depth cap limit Workflow-tool agents?
- Does a review by opus/high find what the work needed? Compare with a fable review on one consequential gate.
- No automatic Fable-to-Opus fallback is documented. The rerun rule is manual.
