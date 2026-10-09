# Scientific Agent Workflow

Status: approved for flexible installation. Runtime readiness checks are recorded separately; no empirical performance advantage has been established.

Use one main agent to own the task and select independent work worth delegating. Sol, Luna and Astra profiles provide starting settings, not a compulsory team or sequence. Choose available agents and methods appropriate to the task within its authorized scope and shared budget. The workflow applies to scientific software, literature synthesis, numerical analysis, and hypothesis development; each project supplies its own validation criteria.

The model allocation, two-attempt escalation threshold, and ten-hour review interval are starting settings to evaluate on real tasks.

## Starting Roles and Model Settings

| Role | Model | Effort | Responsibility and output |
| --- | --- | --- | --- |
| Orchestrator | `gpt-6.1-sol` | `high` | Own the goal, plan, delegation, integration, and completion. Maintain current decisions and verified outcomes. |
| Repository explorer | `gpt-6-luna` | `high` | Locate files, trace code, inspect tests, and report evidence with paths and symbols. Report observations without source edits. |
| Evidence researcher | `gpt-6-luna` | `high` | Retrieve official technical documentation or scientific papers. Return applicable versions, source passages, identifiers, and limitations. |
| Worker | `gpt-6.1-sol` | `medium` | Implement a bounded change and run agreed checks. Return changes, actual results, and unresolved issues. |
| Scientific analyst | `gpt-6.1-sol` | `high` | Synthesize evidence, compare methods, develop hypotheses, and plan analyses. Return supported conclusions, alternatives, and falsifiable predictions. |
| Strategic reviewer | `gpt-6-astra` | `high` | Independently review plans, recurring failures, and completion. Return consequential findings and specific corrections. |
| Computer operator, optional | `gpt-6-luna` | `max` | Complete a bounded application or browser task within permitted actions. Return the observed outcome and evidence. |

These are baseline profiles, not a restriction on using stronger agents for difficult interpretation or implementation. Installed custom profiles pin model and effort; choose a built-in/ad hoc agent with explicit settings when another allocation fits better. Scientific analysts may write scripts and plots and run bounded computations covered by the task. The optional computer operator is not installed by default. A higher effort setting does not establish that an action is low risk.

Codex supports custom role definitions and explicit model and effort settings. Luna supports `max`. Account access and client support must be checked when configuring the harness. [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents), [Luna model specification](https://developers.openai.com/api/docs/models/gpt-6-luna)

## Project Brief and Task Criteria

Keep a short shared brief in the project's existing documentation:

```text
Project objective:
Current task and its contribution:
Deliverables and exclusions:
Scientific assumptions and applicable conditions:
Success criteria and validation methods:
Resources and constraints:
Current artifacts and evidence:
```

A contribution can be a scientific result, reduced uncertainty, or an enabling capability such as a reproducible pipeline. A supported negative result can satisfy the task. The user owns the project objective; agents recommend changes rather than silently replacing it.

For substantial work, connect requirements to observable evidence:

| Requirement | Evidence needed | Current result |
| --- | --- | --- |
| What must be achieved | Check, observation, derivation, or source that can establish it | Met, unmet, or unverified; link to evidence |

Define acceptance criteria before substantial execution. Changes to those criteria require a documented reason grounded in the requirements or new evidence.

## Execution and Coordination

The main agent defines the requested outcome and evidence, chooses methods and delegation, integrates results, and completes the authorized checks and checkpoint. It may investigate, implement or analyze directly. Skip specialist roles and handoffs that add no material value.

Start with one agent. Delegate when work is independent, investigation would crowd the main context, or an independent challenge can detect a consequential defect. Parallelize independent searches and isolated implementation tasks. Keep closely dependent decisions with the main agent. Assign one owner per shared file, dataset or browser session. Choose concurrency within the shared budget. Nested delegation needs explicit assigned ownership and a shared budget; close completed threads.

Give delegates the original requirements, relevant decisions, artifact version, expected evidence, allowed work and resource/stop boundaries. Preserve detailed evidence behind short return summaries. Technical retrieval and literature retrieval may use separate assignments when their scopes differ; scientific analysis does not require a permanent role per subject.

Proceed autonomously through routine choices, agreed checks and authorized checkpoints. Independent work can continue during review. Applicable project authority overrides this generic workflow: preserve explicit pauses, frozen inputs, scientific gates, resource allocations and declared retry limits. Workflow maintenance does not authorize construction, prediction, acquisition or MD. Reviewers support the completion report; only the project's named gates can promote scientific claims.

## Delegation and Return Formats

Every assignment specifies:

```text
Objective and connection to the project:
Scope, necessary context, and artifact version:
Expected output and acceptance checks:
Resource limit and stopping condition:
```

Every return includes:

```text
Result:
Evidence:
Changes:
Uncertainty or unresolved issues:
Recommended next action:
```

Use short summaries with links to detailed artifacts. Preserve decisions, failure history, evidence, artifact versions, completed checks, resource use, active process/agent ownership and the next exact action in project state that survives context resets. Reconstruct current authority and ownership before resuming interrupted work; never repeat a completed step without evidence that its result is stale. An explicit user pause persists until that user explicitly resumes the same objective. Automatic continuation or unfinished state cannot clear it.

## Independent Review Triggers

Use a suitable independent reviewer for plan, recovery or completion when it can detect a material gap or the project requires it. Astra is the starting reviewer profile, not mandatory for every task. Supply a fresh review context with original requirements, necessary decisions, current artifact versions and underlying evidence; do not supply a desired verdict.

| Trigger | Review focus |
| --- | --- |
| Major plan before substantial execution | Goal alignment, omissions, assumptions, feasibility, and whether proposed checks can detect failure. |
| Repeated strategy failure or recurring issue | Failure history, root causes, invalid assumptions, and the smallest useful diagnostic or correction. |
| New evidence invalidates a central assumption | The affected direction and whether further execution remains useful. |
| Optional reminder after ten active task hours | Progress, unresolved risks, evidence quality, and contribution to the objective. |
| Substantial completion where independent review adds value, or where required | Current results against every requirement, missed work, unsupported claims, and project contribution. |

Two materially different failed fixes are an initial diagnostic reminder, not a universal threshold, a requirement to attempt two fixes, or permission to retry a closed run. Review earlier when evidence undermines a central assumption. Preserve project-specific attempt limits. Routine in-scope recovery remains with the main agent.

If using time reminders, record the last review timestamp and check elapsed active time at meaningful checkpoints. Exclude paused time. Ten hours is not a strict timer or execution authority; unattended timing requires harness support.

Independent work can continue during review. Work that depends on a challenged assumption waits for resolution. Astra prioritizes consequential findings and avoids cosmetic changes or unsolicited scope expansion. After correction, review affected findings against the current artifact version.

The reviewer returns:

```text
Disposition: continue, revise, or insufficient evidence
Goal alignment:
Consequential findings with evidence and locations:
Missing verification:
Required corrections and next measurable check:
```

The main agent resolves findings and owns the completion report. Reviewer approval supplements observable checks and scientific judgment; named project gates retain scientific acceptance authority.

## Scientific Verification

Choose verification that fits the task:

| Work | Relevant evidence |
| --- | --- |
| Software | Intended behavior, regressions, integration, and actual outputs. |
| Numerical analysis | Units, reference cases, invariants, convergence, and sensitivity. |
| Statistical analysis | Assumptions, controls, uncertainty, leakage, and repeated-testing effects. |
| Literature synthesis | Source existence, passage support, coverage, conflicting findings, and applicability. |
| Scientific claims | Observable predictions and empirical or mathematical evidence appropriate to the claim. |

Distinguish exploratory findings from confirmatory evidence. Identify inaccessible full text or abstract-only evidence. Match the studied system and conditions before transferring a result to a different setting. Expected results should have an independent justification where possible.

Record inputs, parameters, software versions, randomness, and data behind figures. Preserve failed attempts and negative results. These support reproducibility and make recurring issues diagnosable. [Reproducible computational research](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1003285)

Evaluate the actual outcome, including relevant artifact or environment state. Record checks that were skipped or could not run. [Agent evaluation guidance](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

## Portable Configuration

Keep three layers:

- Harness-specific role files define models, effort, tools, and role boundaries.
- A short global or project instruction file defines routing and Astra triggers.
- A compact scientific workflow skill defines the project brief, handoffs, verification, and completion review.

Reuse existing project documents for the brief and working state. Model bindings belong in the harness adapter; scientific procedures should remain usable with other models and harnesses. Enforce strict timing, resource limits, concurrency, and tool permissions through harness controls when available.

Check effective child permissions rather than inferring them from a profile label. Live parent sandbox settings can override a profile's read-only default. Reader assignments still prohibit edits, but enforced read-only inspection may require a separate read-only parent session without broader runtime overrides. The existing `codex --profile review` provides a standalone inspection path. Run mutating validation in an independently authorized disposable lane. Client runtime settings attest the selected configuration, not server-side model resolution or broad scientific reliability.

Suggested instruction policy:

```markdown
The main agent owns orchestration, integration and completion reporting.

Choose suitable independent work to delegate within the authorized task.
Use the available profiles as defaults; choose methods, available models
and agent count according to the task and shared budget.

Use independent review for consequential assumptions, recurring strategy
failures, invalidated direction and substantial completion where useful.
Project-required reviews remain mandatory. Time and attempt reminders
are heuristics, not execution authority.

Keep independent work moving during review. Resolve consequential
findings before dependent execution or completion.

Require current evidence for success criteria. Preserve scientific
uncertainty and negative results. Parallelize independent work and
avoid competing writers. Keep delegation and reports concise.
```

## Optional Future Independent Evaluation Team

This is an optional future evaluation recipe, not an instruction to launch a team when reading this file. The following assignments are available for a separately scoped session that permits subagent delegation. Each reviewer receives this file and the stated project requirements in a fresh context, forms an assessment independently, and returns findings before seeing other reviewers' conclusions.

| Reviewer | Model and effort | Evaluation scope |
| --- | --- | --- |
| Architecture reviewer | Astra `high` | Goal alignment, role boundaries, context loss, review triggers, failure escalation, resource use, and completion ownership. |
| Scientific verification reviewer | Sol 6.1 `high` | Evidence quality, scientific applicability, falsifiability, statistical validity, reproducibility, and whether task success can be established. |
| Portability and usability reviewer | Luna `max` | Ambiguous instructions, configuration feasibility, duplicated roles, excessive overhead, harness dependencies, and practical use across subjects. |

All reviewers inspect sources relevant to disputed claims. They do not edit the plan. Findings must include severity, section, concrete failure scenario, supporting evidence, and the smallest proposed correction. Distinguish verified facts from recommendations and uncertainty.

Evaluation cases should include a small bug fix, a complex numerical implementation, a literature synthesis with conflicting sources, an observational data analysis, an inconclusive scientific result, a recurring failure, and a long task resumed after context loss.

Use these cases to inspect the plan. An empirical pilot additionally compares the team with Sol alone under comparable time and cost budgets. Track verified completion, missed requirements, rework, latency, cost, and human correction. Repeat representative cases when feasible; a small pilot cannot establish universal superiority.

### Main Thread Handoff

```text
Independently evaluate SCIENTIFIC_AGENT_WORKFLOW.md. Use fresh review
contexts with the original requirements and current document.

Assign Astra high to architecture and strategic review, Sol 6.1 high
to scientific verification, and Luna max to portability and usability.
Set each model and effort explicitly. Reviewers must not edit files
or read each other's conclusions before submitting their own findings.

Require severity, section, failure scenario, evidence, and a minimal
correction for each finding. Include the evaluation cases in the file.
Check primary sources when questioning technical or scientific claims.

As the main agent, reconcile findings using evidence, identify
disagreements, and return a concise assessment plus proposed revisions.
Keep assessment of the written plan separate from claims about runtime
performance. Do not present an empirical pilot as completed unless run.
```

## Research Basis

| Primary source | Application to the workflow |
| --- | --- |
| [Scaling Agent Systems, 2026 revision](https://arxiv.org/html/2512.08296v3) | Coordination benefits depend on task structure; avoid automatic delegation of sequential work. |
| [MAST failure study, 2025](https://arxiv.org/html/2503.13657v3) | Explicit task boundaries, stopping conditions, context preservation, and verification address recurring failure classes. |
| [Anthropic research system, 2025](https://www.anthropic.com/engineering/multi-agent-research-system) | Bounded independent retrieval and clear assignment formats help research coordination. |
| [Cognition engineering critique, 2025](https://cognition.com/blog/dont-build-multi-agents) | Preserve necessary decision context and prevent conflicting implementation choices. |
| [Anthropic long-running harness, 2026](https://www.anthropic.com/engineering/harness-design-long-running-apps) | Use observable completion criteria and adjust review frequency to builder capability. |
| [OpenScholar, Nature 2026](https://www.nature.com/articles/s41586-025-10072-4) | Retrieve supporting passages and inspect citation accuracy, coverage, and unsupported claims. |
| [POPPER, ICML 2025](https://proceedings.mlr.press/v267/huang25n.html) | Translate hypotheses into measurable implications and consider falsification and valid repeated testing. |
| [Matched-budget reasoning study, 2026](https://arxiv.org/abs/2604.02460) | Compare against a single-agent baseline under comparable budgets; more computation can confound apparent gains. |

These sources support workflow principles within their evaluated settings. They do not validate this exact model allocation or establish performance across every scientific field.
