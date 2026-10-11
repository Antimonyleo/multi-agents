# Claude Code adapter

Preserve the existing native definitions in repository-root `agents/scientific_*.md` and their `~/.claude/agents/` links. Codex installation must not replace Claude agents, models, tools or settings.

| Role | Configured model / effort | Ownership and tools |
| --- | --- | --- |
| scientific_explorer | haiku / high | Mechanical lookups; Read/Grep/Glob; no interpretation, logic tracing or writes |
| scientific_researcher | sonnet / medium | One primary-source question; Read/Grep/Glob/WebFetch/WebSearch; no edits |
| scientific_worker | sonnet / medium | Bounded implementation/checks; Read/Grep/Glob/Edit/Write/Bash |
| scientific_analyst | sonnet / high | Evidence synthesis/authorized analysis; same writer tools |
| scientific_reviewer | opus / high | Independent challenge; Read/Grep/Glob only; no shell, writes or jobs |

Inspect the current main settings at setup; they can change outside this skill. The main can own implementation directly. With a Sonnet main, another Sonnet worker needs a useful bounded context/disjoint lane, not duplicate dependent work. With an Opus main, bounded Sonnet execution may save cost, but only if the main integrates rather than repeats it; a cheaper child alone does not prove net savings. Keep interpretation/caller tracing with main/analyst; tiny mechanical lookups use direct tools. Named long jobs need exact commands and authority. Native agents prohibit further delegation; their turn ceilings are not targets.

Call the named role through Agent (`subagent_type`), honoring user-named roles/@agent mentions. A non-fork delegate has fresh context; a fork inherits conversation. Prefer pertinent requirements and versioned evidence for bounded roles, not irrelevant history. For planning, existing `opusplan` or `/model opus` remains available; do not switch main to Opus just to prepare packets then duplicate that work in an Opus delegate.

Per-call model settings normally take precedence. Existing requested-Fable policy allows one disclosed manual Opus rerun if the Fable call errors/is refused/runs another model; it is not a generic outage fallback. Further failure leaves required review unmet. High per-call effort is for harder reasoning, not just long input, runtime or polling. `CLAUDE_CODE_EFFORT_LEVEL` can override role/per-call effort; `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` can override models. Higher-priority definitions, spawn hooks and provider/allowlist substitution can also change routing. Check relevant exposed metadata/setup overrides when they change; do not run all five smoke calls for every skill-only edit.

The installed depth 1/concurrency 3 settings are Agent-tool limits, not universal spend caps. Fork/resume exceptions and workflow/team limits differ; keep task ownership discipline, reserve required review capacity and do not fill slots. Installation never merges settings. Do not change native defaults without quality evidence.

Opus reviewer gets scoped diffs and terminal command-output files because it has no shell. Ask one decision-focused pass with actionable severity/evidence, disposition and next checks; scope without hiding counterevidence. Avoid speculative full-repo searches or routine status/check questions. Concise final findings do not cap hidden thinking. Prefer native background completion over repeated progress messages/resumes.

Use [maintenance.md](../maintenance.md) for affected-role checks after actual CLI/profile changes. Current configuration and earlier checks do not prove new-session dispatch. Sources: [Claude subagents](https://code.claude.com/docs/en/sub-agents), [cost guidance](https://code.claude.com/docs/en/costs).
