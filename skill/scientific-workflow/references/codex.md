# Codex adapter

Use native Codex orchestration. The source profiles live in `agents/codex/` at the repository root; installation copies them into `~/.codex/agents/`. The shared skill is linked under `~/.agents/skills/scientific-workflow/`.

| Role | Configured model / effort | Ownership |
| --- | --- | --- |
| scientific_explorer | gpt-6-luna / high | Locate files, trace specified callers/tests and extract bounded facts |
| scientific_researcher | gpt-6-luna / high | Retrieve primary sources and applicable passages/versions |
| scientific_worker | gpt-6.1-sol / medium | Implementation, instrumentation, execution, debugging, evidence capture and named checks |
| scientific_analyst | gpt-6.1-sol / high | Difficult analysis and evidence synthesis when warranted |
| scientific_reviewer | gpt-6-astra / high | Consequential planning and independent review |

These are the user's defaults, not a demonstrated universal model ranking. Sol medium owns most execution. Sol high is for harder analysis, not the default probe runner. Luna support must be bounded enough to save Sol work. Do not route all reading, writing or execution to Luna. Explorer/researcher profiles are reader assignments. A narrowly specified mechanical write needs an explicitly authorized writer with suitable tools, not a silent conversion of a reader role. Ambiguous interpretation, method selection, optimizer instrumentation and recovery decisions return to Sol.

Custom profiles pin their model and effort; spawn arguments do not override those bindings. For a different authorized allocation, use an available built-in/ad hoc role with explicit settings. Record role, configured settings, owner and permitted paths before dispatch or reuse. Check runtime evidence if exposed and state unavailable or unverified settings honestly.

Use the configured `scientific_reviewer` for consequential Astra high planning/review. It may return a plan for Sol or the coordinator to persist; it does not need write access. Reserve thread capacity for mandatory review. Reuse a thread only when its model, scope and context suit the new task; consequential completion after planning requires a fresh reviewer context.

If Astra is unavailable, the Astra requirement stays unmet. Continue only independent work that does not depend on it. Do not substitute an unknown model, label generic review as Astra, or start standalone sessions/export evidence/enlarge budgets to evade limits without authority. An alternative requires explicit user or applicable project authority and disclosure.

Parent policy can override a custom profile's read-only baseline. A reader assignment still prohibits writes, but a role name does not prove OS isolation. For enforced review isolation, use a separate read-only parent such as an existing `codex --profile review`, without broader overrides, and verify effective policy. Mutating validation belongs in an authorized disposable lane.

Codex context inheritance depends on the harness (`fork_turns` where supported). Give enough requirements and evidence for the assignment; do not assume either full history or no history. Model/effort overrides may require a history-free fork in a given harness. Respect its advertised schema and concurrency limits. Close only completed owned threads when supported, preserving receipts; do not interrupt another session's work.

Installed copies deliberately remain regular TOML files, matching the previously validated discovery shape. `scripts/install.sh --target codex --check` detects source/copy drift. Restart the session after profile changes. Static validation does not prove the new session's live model routing.
