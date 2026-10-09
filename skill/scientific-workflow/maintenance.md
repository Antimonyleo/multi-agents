# Maintenance for the scientific-workflow skill

## Where things live

| Item | Location |
| --- | --- |
| Agent definitions | `agents/scientific_*.md` in the source repo, linked into `~/.claude/agents/` |
| Spawn caps, Sonnet effort | `~/.claude/settings.json` (`env`, `modelSettings`) |
| Routing rules (this skill) | `skill/scientific-workflow/` in the source repo, linked as `~/.claude/skills/scientific-workflow` |
| Source repo | `~/githubrepo/scientific-workflow-skill` (edit here; `scripts/install.sh --check` verifies the links) |
| Benchmarks | `benchmarks/2026-10-08/` in the source repo (protocols, `bench.py`, data, `RESULTS.md`) |
| Project review gates | each project's guidance, for example `docs/agent_guidance/delegation.md` |
| Codex counterpart | `~/.codex/agents/*.toml`, `~/.agents/skills/scientific-workflow/`. Same role names, separate files. Update both when roles change. |

## Check after any change or Claude Code update

Run a fresh headless session in a scratch folder. Call each role once with a trivial task, with a main model different from the role's model:

    claude -p "Call scientific_explorer, then scientific_reviewer ... each once. Task: Reply with the single word OK. Use no tools." \
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

## Open questions

- Can the reviewer run at medium effort (the Opus 5.5 default) and still find what high finds? Its cost was 3 to 5 times a whole small task.
- Does the workflow help on a long task (tens of turns, large context)? Not tested; the benchmark tasks were all under $0.40.
- Does `scientific_explorer` ever pay? It was never invoked in 38 runs.
- Is medium enough for worker and researcher on real tasks? Run a sweep on two or three real tasks.
- Does Haiku/high do mechanical lookups without errors? Spot-check the first few results against the files.
- Does the concurrency cap or depth cap limit Workflow-tool agents?
- Does a review by opus/high find what the work needed? Compare with a fable review on one consequential gate.
- No automatic Fable-to-Opus fallback is documented. The rerun rule is manual.
