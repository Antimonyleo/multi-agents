# Codex adapter

Use native Codex orchestration. Repository `agents/codex/*.toml` installs as regular files under `~/.codex/agents/`; the shared skill links under `~/.agents/skills/`.

| Role | Configured model / effort | Ownership |
| --- | --- | --- |
| scientific_explorer | gpt-6-luna / high | Bounded file/caller/test discovery and specified facts |
| scientific_researcher | gpt-6-luna / high | Bounded primary-source retrieval with passages/versions |
| scientific_worker | gpt-6.1-sol / medium | Implementation, instrumentation, execution, debugging and evidence/checks |
| scientific_analyst | gpt-6.1-sol / high | Hard analysis/evidence synthesis |
| scientific_reviewer | gpt-6-astra / high | Consequential planning and independent review |

The main session defaults to Sol/high and may own dependent execution directly. Sol/medium delegation needs a useful bounded lane; avoid duplicate coordinator/worker investigation. Sol/high analyst is not the default job runner. Luna must save substantial owner work; known tiny lookups use direct tools. Explorer/researcher are reader assignments. Mechanical writes need an explicitly authorized writer with suitable tools, not a silent reader-role conversion. Method selection, optimizer instrumentation, interpretation and recovery stay with Sol.

These defaults are user policy, not a measured universal ranking. Custom profiles pin model/effort; spawn arguments do not override them. A different authorized allocation needs a supported built-in/ad hoc role with explicit settings. Record role, configured settings and scope; inspect exposed metadata when necessary, not through repeated model-identity questions. Parent policy may override read-only defaults. For enforced inspection isolation, use a separate read-only parent such as an existing `codex --profile review` and verify effective policy; mutating checks belong in an authorized disposable lane.

Use Astra/high for consequential review with a decision-focused packet. It can return a plan for the coordinator/Sol to persist without write access. Reserve capacity; completion after plan authorship needs fresh reviewer context. If unavailable, the Astra requirement stays unmet: continue only independent work, no silent substitute or session/budget bypass. An alternative needs user/project authority and disclosure.

Respect native context/concurrency schemas. Prefer fresh bounded support/review (`fork_turns` where supported); inherit history only when needed. Reuse suitable owned execution context instead of repeated full-history forks. Model/effort overrides may require a history-free fork in this harness. Close only completed owned threads when supported, retaining receipts.

Use native long-running tools and one progress owner; status is not another assignment. Profile copies preserve the previously validated discovery shape. `scripts/install.sh --target codex --check` detects drift; reload sessions after profile changes. Defaults stay unchanged pending quality evidence for another allocation. Static checks do not establish fresh live routing or effective OS isolation.

Source: [OpenAI subagent guidance](https://learn.chatgpt.com/docs/agent-configuration/subagents).
