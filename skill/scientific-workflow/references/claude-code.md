# Claude Code adapter

Preserve the existing native definitions in repository-root `agents/scientific_*.md`, linked under `~/.claude/agents/`. The shared skill supports Claude; Codex installation must not replace or rewrite these agents, links or settings. Do not make Claude conform to Codex profiles.

| Role | Configured model / effort | Ownership and tools |
| --- | --- | --- |
| scientific_explorer | haiku / high | Mechanical lookups only; Read, Grep, Glob; no interpretation, logic tracing or writes |
| scientific_researcher | sonnet / medium | One bounded primary-source question; Read, Grep, Glob, WebFetch, WebSearch; no edits |
| scientific_worker | sonnet / medium | Bounded implementation and named checks; Read, Grep, Glob, Edit, Write, Bash |
| scientific_analyst | sonnet / high | Evidence synthesis and authorized analysis; Read, Grep, Glob, Edit, Write, Bash |
| scientific_reviewer | opus / high | Independent review; Read, Grep, Glob only; no shell, edits or jobs |

The existing setup uses Sonnet 5.5 high in the main thread and `opusplan` or `/model opus` for planning. This reference describes that setup; applying the skill does not change it. The optional settings snippet specifies concurrency 3 and depth 1. Installation never merges `settings.json`. Verify effective limits; native agents prohibit further delegation.

Keep logic tracing, mapping tests and interpretation with the main thread or analyst. The explorer only finds/counts/lists specified items and returns filtered evidence. Writers may run only checks/jobs covered by the brief; a long job needs the exact command and resource authority.

Call the role by name with the Agent tool (`subagent_type`). If the user names a role or `@agent-scientific_reviewer`, dispatch that exact role. Delegates have no conversation history: give the necessary requirements, decisions, authority, identities and boundaries explicitly.

Existing Claude policy allows per-call settings to override the agent file. For a requested Fable review, pass `model: "fable"`; if the call errors, is refused or runs another model, manually rerun once with `model: "opus"` and disclose it. This fallback is Claude-specific and does not grant a Codex/Astra fallback. For harder or longer worker/researcher tasks, pass `effort: "high"` when supported.

Use `scientific_reviewer` at the shared consequential review gates and project-required/user-requested reviews. Prepare diff and command-output files before dispatch because it has no shell. It reports findings with severity and a disposition; the coordinator integrates them. Do not ask it to execute tests or supply missing terminal evidence. Use a fresh context for independent consequential completion when the plan author participated earlier.

For live model checks after an agent or CLI change, use the procedure in [../maintenance.md](../maintenance.md). Existing recorded model checks and benchmarks describe earlier Claude runs, not new verification of this merged skill. Preserve native max-turn/tool restrictions and the manual model-fallback rule.
