# Coding Guide

Use this guide for implementation style. [AGENTS.md](AGENTS.md) is the current
repository contract; explicit user instructions take precedence. Follow its
scientific authority, execution boundaries and required completion checks.

## Establish the change

- Read the affected implementation, its immediate callers and relevant tests
  before editing. Reuse existing utilities and public interfaces.
- State the expected outcome and the smallest check that can falsify it. For
  optimizer work, read the
  [execution policy](docs/agent_guidance/optimizer_execution_policy.md) first.
- Infer routine choices from existing code, tests and current plans. Ask only
  when missing information materially changes the outcome or authority.
- Resolve conflicting conventions using the current contract and tested caller
  behavior. Explain material tradeoffs; do not silently blend incompatible rules.

## Keep the implementation focused

- Make the smallest complete change that satisfies the request. Avoid speculative
  features, single-use abstractions and unrelated refactoring.
- Match the surrounding naming, layout and error-handling conventions. Prefer
  one focused module per concern over extending an oversized file.
- Preserve unrelated dirty-worktree changes. Remove imports and code made unused
  by your own change; leave unrelated cleanup for a separate task.
- Use ordinary code for deterministic transforms, routing, retries and status
  handling. Introduce model calls only when judgment is part of the requirement.
- Preserve lazy backend imports, bounded process counts, deterministic seeds and
  stable result ordering. Avoid nested thread oversubscription.

## Verify the intended behavior

- Test observed failures and meaningful requirements, including relevant negative
  cases. Tests should fail when the requirement is violated, rather than mirror
  the implementation or assert incidental constants.
- Run the checks required by AGENTS.md for the kind of change. Optimizer code
  requires its full completion checks; documentation and configuration maintenance
  require syntax, references, discovery and preservation checks.
- When NUPACK or ViennaRNA behavior changes, include the required real-backend
  integration check. A mock or process exit cannot establish scientific quality.
- Preserve the distinction between optimization completion and quality acceptance.
  Do not infer convergence, accepted designs or whole-target folding from a
  partial diagnostic.
- After required checks pass, broaden testing only to resolve a concrete remaining
  concern. Do not add tests for reversible low-impact edits that need no new
  behavioral coverage.

## Finish and report

- Complete authorized work through its named validation and checkpoint. Preserve
  explicit pauses, frozen scientific inputs and scope boundaries.
- Give brief progress updates when findings or decisions matter. Keep session
  state in the current handoff and reusable evidence-backed lessons in the
  relevant research document.
- Report what changed, why, what was verified and any material limitation. Name
  failed, unavailable or skipped required checks; do not call them passed.
- Keep measured results separate from plans, hypotheses and unsupported claims.

The [previous guide](docs/agent_guidance/coding_guide_2026-09-30.archive.md) is
preserved unchanged for historical reference and is not current instruction.
