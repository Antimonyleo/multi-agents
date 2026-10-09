# scientific-workflow-skill

A Claude Code workflow for daily scientific work: a routing skill (`scientific-workflow`)
and five sub-agents (`scientific_explorer`, `_researcher`, `_worker`, `_analyst`,
`_reviewer`) with a model and effort for each, plus the benchmark that tests it. This repo
is the single source of truth. The live copies under `~/.claude` are links to it.

## Layout

| Path | What it is |
| --- | --- |
| `skill/scientific-workflow/SKILL.md` | The skill: roles, when to delegate, review gates, brief, overrides. |
| `skill/scientific-workflow/maintenance.md` | Where things live, the model-check procedure, evolution log, open questions. |
| `agents/scientific_*.md` | The five agent definitions (model, effort, tools, rules). |
| `settings/settings.snippet.json` | The `settings.json` keys the workflow depends on (spawn caps, Sonnet effort). Merge by hand. |
| `benchmarks/2026-10-08/` | Protocols (frozen before each phase), `bench.py` harness, ground-truth scripts, per-run data, `RESULTS.md`. |
| `scripts/install.sh` | Links the skill and agents into `~/.claude`. `--check` and `--uninstall` also work. |

## Install on a machine

    scripts/install.sh            # link skill and agents into ~/.claude
    scripts/install.sh --check    # confirm the links
    scripts/install.sh --uninstall

The script never overwrites a real file; it skips and says so. It does not touch
`settings.json`: merge `settings/settings.snippet.json` yourself.

## Improve the workflow

1. Edit files here. The links make the change live. Skill edits are picked up in a running
   session; restart the session after changing an agent file.
2. After any change to an agent, the settings or a Claude Code update, run the model check in
   `skill/scientific-workflow/maintenance.md`.
3. Add a dated line to the evolution log in `maintenance.md`. Record what changed and why.
4. To test a change, add a new dated folder under `benchmarks/`, write its protocol before
   running, and keep failed criteria as results. Have a fresh reviewer check any seeded ground
   truth first (two of mine were wrong in the first benchmark).
5. The main thread must not edit the skill or agents on its own; it proposes, you approve.

## Status (2026-10-08)

50 headless runs, about $18 at list price. The workflow costs about 3 to 8% more than plain
Sonnet when idle or invoked, never delegated by itself on small tasks, and is about half the
cost of Opus alone on small tasks only because its main thread is Sonnet. A review routed to
`scientific_reviewer` cost 4 to 5 times a small task and found nothing extra. Saving tokens
and keeping long tasks on track are untested. See `benchmarks/2026-10-08/RESULTS.md` and the
open questions in `maintenance.md`.

## Not in this repo

- `~/.claude/settings.json` (only the snippet).
- The project gate file for origamifolder7, `docs/agent_guidance/delegation.md` in that project,
  and its `AGENTS.md` pointer. They name that project's required reviews.
- The Codex counterpart: `~/.codex/agents/*.toml` and `~/.agents/skills/scientific-workflow/`.
  Same role names, separate files. Update both when roles change.
- Raw run logs (`run.jsonl`) and the generated fixtures. `bench.py build` rebuilds the fixtures.
  `bench.py` has machine-specific paths: it builds fixtures from `/home/hao/folding/origamifolder7`.
