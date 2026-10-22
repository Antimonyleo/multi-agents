# multi-agents

A scientific workflow for **Codex and Claude Code**. One agent owns the task;
other agents help with specific work or review important decisions.

## Why use it?

An agent can stop halfway through a long task, repeat a helper's work, or report
success without checking the result. The rules here address those problems:

- One owner handles implementation, checks and handoff.
- Helpers take independent work with a clear expected result.
- Reviewers check important decisions and results.
- Checkpoints record progress; pauses, budgets and required approvals still apply.

Use it for research software, analysis and experiments spanning several steps
or sessions. Simple edits stay with the main agent.

## Agent setup

Five optional roles are included. Their names start with `scientific_`.

| Role | Job | Claude model / effort | Codex model / effort |
| --- | --- | --- | --- |
| Explorer | Find files and facts | Haiku / high | gpt-6-luna / high |
| Researcher | Retrieve primary sources | Sonnet / medium | gpt-6-luna / high |
| Worker | Write code and run checks | Sonnet / medium | gpt-6.1-sol / medium |
| Analyst | Analyze evidence and methods | Sonnet / high | gpt-6.1-sol / high |
| Reviewer | Review assumptions and results | Opus / high | gpt-6-astra / high |

Each runtime keeps its own tools and permissions. The [Claude](skill/scientific-workflow/references/claude-code.md)
and [Codex](skill/scientific-workflow/references/codex.md) notes explain the setup.

## Install

You need Python 3.11+, a working Codex or Claude Code installation, and access to
the configured models.

```sh
git clone https://github.com/Antimonyleo/multi-agents.git
cd multi-agents
scripts/install.sh --target both --dry-run
scripts/install.sh --target both
scripts/install.sh --target both --check
```

Use `--target claude` or `--target codex` to install for one runtime.

The installer links the skill and Claude agents, and copies Codex profiles.
It leaves runtime settings and the main model unchanged. Keep this checkout
in place because installed links point here. Start a new session afterward.

Conflicting files stop installation. `--migrate` backs them up before replacing
them; `--rollback RECEIPT` undoes an installation. See `scripts/install.sh --help`.

## Use it

Ask for the skill by name and give it a task, for example:

> Use scientific-workflow to fix the failing parser tests. Finish the agreed
> checks and Git checkpoint. Delegate independent work when useful.

For project discovery, add a short pointer to `AGENTS.md` using the installed or
bundled skill's actual path:

> For substantial multi-step execution or recovery after context loss, use
> scientific-workflow, including for single-agent work. Reuse this project's
> plan, acceptance checks and pause boundaries.

Keep project-specific scientific gates locally. If a project bundles its own copy,
record its upstream revision and local differences beside that copy; update it
through the project's normal review. A shared installation does not update bundles.

Ordinary long tasks use the existing checkpoint. Hooks and strict receipts are
optional unless an existing binding or project gate requires them. Judge adoption
by forgotten items, unnecessary stops, recovery errors and duplicated helper work
in normal authorized tasks; skill invocation alone is not a success measure.

Read the [skill](skill/scientific-workflow/SKILL.md) for the rules and
[maintenance guide](skill/scientific-workflow/maintenance.md) for checks. The
[long-task study](benchmarks/2026-10-13-long-task-retrospective/REPORT.md) records
the evidence so far. Better outcomes and lower whole-task cost remain unproven.

Historical benchmark scripts may need local path changes.
