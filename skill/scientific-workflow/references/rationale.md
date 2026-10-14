# Rationale and evidence limits

One execution owner reduces coordination for dependent steps. Bounded independent extraction and fresh consequential review can still help. Agent count, effort and elapsed time do not establish quality. The runtime adapters preserve user-selected model allocations; they are not cross-provider rankings.

The 2026-10-08 Claude benchmark is retained unchanged in repository-root `benchmarks/2026-10-08/`. Its 50 small-task runs do not establish long-task savings or a Codex comparison. See its `RESULTS.md` for costs, seeded-truth corrections and limitations.

A paused Project 2 run exposed premature review calls, repeated task/status packets, wait/message cycles and overlapping inspection. It also required real scientific debugging and broad validation. Improve coordination without removing required checks or claiming all consumption was avoidable. Cached input, uncached input, output and reasoning tokens must be distinguished; reasoning is a subset of output, not an additional charge. No savings estimate follows from changing this skill.

The 2026-10-13 retrospective of 27 long sessions (`benchmarks/2026-10-13-long-task-retrospective/`) found that the user had to say "do not stop" after the agent stopped part-way through assigned work in 12 to 14 sessions (two coders). This motivates the rule that a checkpoint is not a stop. It is observational; the effect of the rule is unmeasured.

[OpenAI multi-agent guidance](https://developers.openai.com/api/docs/guides/responses-multi-agent) discusses token overhead and poor fits for dependent work or a dominant slow operation. [Anthropic's agent guidance](https://www.anthropic.com/engineering/building-effective-agents) supports simple orchestration and evaluators with clear criteria. [Outcome-based evaluation guidance](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) supports checking outcomes rather than wording.

The prior Codex skill and home manual are preserved under repository-root `docs/migration/2026-10-09/` for provenance only. They are historical snapshots, not competing active policy. Project-specific scientific predicates, resource allocations and pauses remain in project authority, not in this generic skill.
