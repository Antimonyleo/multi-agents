---
name: scientific-workflow
description: Coordinate substantial scientific software, analysis, literature or hypothesis tasks with Luna for bounded mechanical support, Sol for implementation and execution, and Astra for consequential planning and independent review. Preserve project authority and resumable checkpoints; small tasks need no team.
---

# Scientific workflow

Own the requested outcome through its authorized checks and checkpoint. Read the project's current plan/handoff and relevant authority before execution. Reuse existing task state. If needed, write a compact contract: deliverable, scope, authority, checks, resource envelope, stop boundaries and next action. Match each substantial requirement to evidence that can establish it.

## Choose the execution shape

Use native Codex orchestration. Work alone when that is sufficient. Delegate independent work when parallel execution, context isolation or an independent challenge can materially improve the result. Keep closely dependent reasoning and integration in the main thread. This skill requests suitable delegation within the user's authorized task; it does not expand scope, resources or permissions.

The main agent owns requirements, dispatch, integration, evidence and completion. Use the following task allocation unless the user explicitly chooses another allocation. These are workflow defaults, not a claim that this exact model hierarchy has been benchmarked.

| Agent | Model / effort | Default ownership |
| --- | --- | --- |
| scientific_explorer | gpt-6-luna / high | Locate files, trace callers and tests, extract specified facts |
| scientific_researcher | gpt-6-luna / high | Retrieve primary sources and report applicable passages and versions |
| scientific_worker | gpt-6.1-sol / medium | Implementation, probe instrumentation, execution, debugging, evidence capture and named checks |
| scientific_analyst | gpt-6.1-sol / high | Difficult evidence synthesis or analytical reasoning when the assignment needs it |
| scientific_reviewer | gpt-6-astra / high | Establish or challenge consequential plans; independently review assumptions and completion evidence |

Route by reasoning demands and decision ownership, not file operations. Sol reads and writes the files needed for its implementation. Luna may do narrowly specified mechanical edits with explicit file ownership and appropriate permitted tools; the installed explorer/researcher profiles remain reader assignments. Luna does not own method selection, algorithm changes, optimizer instrumentation, scientific interpretation or recovery decisions under these defaults. If a mechanical assignment becomes ambiguous or needs such decisions, return the finding to the coordinator and transfer the affected work to Sol. Do not make Luna the implementation owner merely because it already has the files or environment open.

Use Sol medium for most execution. Use the Sol high analyst only when harder analysis warrants it; it is not the default probe runner. Astra may return a plan proposal in its reply, which the coordinator or Sol persists. Planning does not require giving the reviewer write access. Do not change the main session's model or global configuration merely to apply this allocation.

These custom profiles pin their model and effort. Spawn arguments do not override those bindings. For a different authorized allocation, choose an available built-in/ad hoc agent with explicit settings. Before dispatch or reuse, record the role, configured model and effort, task owner, permitted paths and required review. Check available runtime evidence when it is exposed; a name or agent narrative alone is not model provenance. Report unavailable or unverified settings honestly, without claiming server-side model identity from configuration alone.

Inspect the effective child permissions when isolation matters. Live parent sandbox settings can override a custom profile's read-only default. A reader assignment still prohibits edits, but its name does not establish OS-enforced read-only access. For enforced inspection isolation, use a separate read-only parent session (such as the existing `codex --profile review`) without broader permission overrides, and verify the effective policy. Run any needed mutating checks in a separately authorized disposable validation lane.

Choose the number of agents from independent work and the shared budget, not elapsed task duration. Keep tightly dependent implementation and reasoning with one Sol owner; parallelize bounded retrieval or disjoint implementation only when it helps. Do not require every role or a permanent team. Nested delegation needs assigned ownership and a shared budget.

Give each delegate a compact packet: objective and expected output; original requirements and necessary decisions; exact input/artifact identities; allowed tools and owned paths; named acceptance checks; resource/retry limits; stopping conditions; and evidence to return. Provide enough context to decide correctly without copying unrelated conversation history. Give each writer exclusive paths or a worktree. Delegates return evidence paths, actual changes and checks, uncertainties, and the next exact action; the coordinator verifies consequential results against those artifacts.

Plan thread capacity for required Astra review before filling worker slots. Close only completed threads owned by this task when the harness supports closure; preserve their receipts and never interrupt another session's work to make room. Reuse an agent only after checking its model, scope and context suitability. If Astra cannot launch, keep the Astra review requirement unmet and continue only independent work that does not depend on it. Do not silently replace it with an agent of unknown model or report generic independent review as Astra review. Use an alternative only when the user's instructions or applicable project authority authorize it, and report the substitution. Do not start extra standalone sessions, export evidence or enlarge resource budgets to evade a thread limit without authority for that action.

## Execute and review

Choose methods and implementation details autonomously within authority. Continue runnable work through named checks and the authorized checkpoint without repeated permission requests. Independent work may continue during review; work that depends on a challenged central assumption waits for resolution.

For a substantial scientific plan, use Astra high to establish or challenge the objective, assumptions, method, controls, required observables, resource limits and stopping criteria before costly or consequential execution. Reuse a current reviewed plan when its inputs, assumptions and checks still apply; routine implementation choices do not need another planning cycle. Sol owns implementation and execution through the named checks and checkpoint. Luna supplies bounded support when useful.

Use Astra high for independent review of recurring strategy failures, evidence that invalidates the direction, claim-authority changes and substantial completion where review can detect a material gap. Project-required reviews remain mandatory. Give the reviewer a fresh context containing original requirements, necessary decisions, exact artifact versions and underlying evidence, without a desired verdict. When Astra authored the plan, consequential completion review should use a fresh reviewer context that can challenge that plan; planning participation alone does not count as independent completion review. Integrate consequential findings and check affected evidence. Reviewer approval is not scientific acceptance.

Before a costly probe, Sol checks that the execution lane captures the observables named by the plan, including failures and termination. When an optimizer or wrapper can substitute a fallback, retain the raw proposal and selected output separately with their units, scales, identities and decision reasons. Review feedback does not authorize another scientific attempt: apply corrections and rerun affected checks only within the existing resource and retry envelope, or report the unmet requirement.

Two materially different failed fixes and ten active task hours are optional diagnostic reminders, not universal stopping rules, retry authority or strict timers. Consider review sooner when evidence demands it. Unattended timing requires harness support. Preserve the project's declared retry limits, and do not retry unchanged terminal failures.

## Evidence and recovery

Verify actual artifacts or environment state, not the agent's narrative. Record exact inputs, versions, parameters, randomness, checks and output paths as appropriate. Match conclusions to the studied system and conditions. Check units/reference cases/convergence for numerical work; assumptions/controls/leakage/repeated testing for statistics; source existence/passages/coverage/conflicts for literature. Separate exploratory findings from confirmatory evidence. Preserve negative results and failed attempts. Report skipped checks and unresolved evidence.

At meaningful checkpoints, persist completed checks, artifact versions, decisions, failures, resource use, active process/agent ownership and the next exact action in the existing handoff. After interruption or context loss, reconstruct current authority and ownership from disk; preserve completed work, inspect any live owned jobs and resume only the earliest incomplete authorized task.

An explicit user pause persists until that user explicitly resumes the same objective. While paused, perform only the requested closure, inspection or review. Do not delegate, edit implementation, run tests/executors or allocate outputs for the paused objective. Automatic continuation, elapsed time and unfinished state cannot clear a pause. A separate authorized workflow test does not resume a scientific objective.

Only project gates can promote scientific claims. A generic PASS, reviewer disposition, configuration or fixture result is not accepted-design, whole-fold or scientific success. Close owned work when returning; preserve other sessions' jobs and edits. Report the result, evidence, material limitations and next exact action concisely.

For the longer rationale, read [the full workflow](/home/hao/SCIENTIFIC_AGENT_WORKFLOW.md) when needed. Its older flexible allocation examples do not replace the dispatch defaults stated here. Native agent files bind models and permissions; this skill supplies routing instructions, not runtime enforcement. Other assistants must use their own supported adapters while preserving project authority.

## Basis and validation

[OpenAI subagent guidance](https://learn.chatgpt.com/docs/agent-configuration/subagents) supports narrow roles, explicit model/effort settings, Luna for lighter work and Sol for demanding execution. [Anthropic's workflow guidance](https://www.anthropic.com/engineering/building-effective-agents) supports simple orchestration and evaluators with clear criteria. Its [multi-agent research account](https://www.anthropic.com/engineering/multi-agent-research-system) supports bounded task packets and delegation proportional to task complexity. [Scaling-agent research](https://arxiv.org/abs/2512.08296v3) finds that coordination benefits depend on task structure. These sources support the workflow principles; the Astra high planning/review allocation is the user's chosen policy, not a demonstrated universal model ranking.

Validate skill structure and referenced profiles after edits. Walk through mechanical extraction, probe development, substantial planning/completion, an unavailable reviewer, a paused task and a small local change. Check the intended ownership, evidence and stop boundaries. Static checks or manual walkthroughs do not prove live dispatch behavior. When live evaluation is separately authorized, inspect actual tool traces and final artifacts under a matched budget, using [outcome-based evaluation guidance](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents); do not grade routing by agent names or wording alone.
