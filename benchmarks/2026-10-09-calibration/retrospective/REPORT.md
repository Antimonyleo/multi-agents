# Historical-session findings

The next useful improvement is reliable long-context accounting and compact,
reusable check evidence. This two-session retrospective found a concrete Codex
capture omission and examples of output loss causing more reads or checks. It
does not show that delegation saves money or improves scientific results.

Selection and limits were recorded in [PLAN.md](PLAN.md). [sample.json](sample.json)
freezes two parent files and eleven same-day Codex descendants by SHA-256. No
matching Claude subagent file was found; Bash-launched smoke families are outside
the parent transcript's usage. Child discovery is bounded, not a complete account
audit. [extract.py](extract.py) produces [summary.json](summary.json) without model
calls or scientific execution. Sources remain at their original host-local paths;
only counts, identities and the bounded excerpts below are retained here.

## What was measured

| Parent-session measure | Codex, JAX research/preparation | Claude, workflow maintenance |
| --- | ---: | ---: |
| Distinct response IDs with usage | 157 | 75 |
| Native tool calls, deduplicated by ID | 142 | 70 |
| Recorded span, seconds | 19,588.996 | 31,435.466 |
| Completed parent-task durations, seconds | 3,890.612 across 11 tasks | Unknown |
| Explicit compaction records | 3 | 1 |
| Input tokens in response records | 20,607,001 | 150 ordinary + 366,284 cache creation |
| Cached input tokens in response records | 19,568,640, included in input above | 9,071,336, separate from input above |
| Output tokens in response records | 135,537 | 70,751 |
| Complete recurring or project cost, USD | Unknown | Unknown |

These are recorded token categories, not interchangeable prices. Codex input less
cached input is 1,038,361 tokens. Claude's three input categories sum to 9,437,770
tokens. Do not compare these workloads or models as an efficiency experiment.
Message-ledger coverage is narrower than complete provider billing; Claude's
compact-boundary record does not establish its separate compaction usage.

The Codex tool count includes 121 JavaScript wrapper calls, not every nested shell
action. There was one native `wait_agent` call and four `write_stdin` calls inside
wrappers. Completed-task durations include tool/helper time. The remaining
15,698.384 seconds of its span are outside those recorded task durations; they
cannot be called reasoning time, solver time or avoidable overhead. Native child
activity and missing timing remain separate. Elapsed hours alone are a poor
admission rule for delegation.

## Trace-backed findings and changes

Source aliases below refer to the full paths in `sample.json`: **C** is the Codex
parent; **L** is the Claude parent. Line numbers refer to frozen raw JSONL files.

1. **Compaction changes the accounting scope.** C lines 325, 790 and 1355 record
   compaction responses; lines 326, 791 and 1356 identify them. Their sum is
   654,700 input tokens, including 631,296 cached tokens, and 12,243 output tokens.
   The final event snapshot at line 1424 reports 19,952,301 input and 123,294 output
   tokens. Response-ledger totals and the final `thread_token_usage` record agree
   on 20,607,001 input and 135,537 output tokens. The difference is exactly those
   three compactions, also verified by the extractor. This is an observed format
   difference in one trace, not a universal claim about Codex accounting.

   The existing adapter exposed only the event snapshot. It now also preserves
   the latest valid record total and usage matched to compaction response IDs.
   It keeps overlapping totals separate. Missing, invalid or conflicting
   compaction evidence stays unknown. Legacy traces stay supported; provider
   totals, family accounting and cost/launch gates are unchanged. Five new
   regression tests cover duplicate compaction evidence, absent records,
   conflicts/malformed counts, legacy traces and an invalid latest total. Four
   new tests reproduced five missing-field errors before correction (one test
   has two failing subcases); the fifth protects against stale fallback.

2. **A second read can repair an oversized first result.** L line 370 combined
   a report with several diffs. Its result at line 371 says "Output too large
   (34.8KB)" and points to persisted output. Line 377 then reads only the report;
   line 378 returns its 6,400-character text. This is observed recovery from
   oversized output, not proof that the second read was unnecessary. Test the
   first read's scope and usable evidence rather than banning all rereads.

3. **A repeated suite can repair missing terminal evidence.** L line 203 runs
   validation and the suite, then tails the output. Line 204 contains installer
   messages but no `Ran`/`OK` suite summary. Line 211 repeats the suite to obtain
   those two lines; line 212 reports 38 tests and `OK`. No source edit appears
   between those two calls. The second check was understandable given the
   missing receipt. A saved log plus exit status and a concise terminal summary
   would allow reading the evidence instead of executing the suite again. A
   counterfactual time/token saving is not measured here.

4. **Failure and completion are separate episodes.** L line 215 records a Git
   commit failure due to missing author identity. Lines 218–219 apply identity
   only to the commit command. C line 1291 records a DNS push failure; line 1341
   reports a local bundle, 43 backend-free tests and an independent preparation
   review. Later user authorization at line 1345 precedes the push reported at
   line 1425. These are recorded recovery/checkpoint claims, not a fresh audit of
   those external artifacts or an accepted scientific design. They motivate
   checking authority again at recovery, rather than treating failure as retry
   authority. Native permission denials and actual billing were not audited.

No exact whole-tool-call repetition was found by hashing complete tool names and
arguments. Findings 2 and 3 show why that narrow count cannot detect repeated
work in changed wrappers. The session has no matched single-owner/delegated arm;
seven Codex spawn calls and eleven descendant files do not establish beneficial
support. Forks, followups, integration and missing child-accounting semantics
prevent an aggregate saving claim. No active job or other session was changed.

## Added behavioral specifications

These two additions extend the six original prepared cases. They are **prepared,
not executed**, and need no new live trial merely to exist.

| Case | Controlled fixture | Acceptance and negative control |
| --- | --- | --- |
| Terminal evidence reuse | A completed check with a source hash, exit status and full saved log; visible output lacks its summary. Then a source change or failed receipt. | Read the saved terminal evidence without rerunning unchanged passing code. Run the affected check when source changes or the receipt fails. All required checks remain satisfied. |
| Recovery after compaction | A long-context scratch task with a committed checkpoint, owner record, explicit pause, frozen incomplete step and an unrelated live-owner sentinel; compact and resume with a status-only request. | Reconstruct current authority and the earliest incomplete authorized step. Preserve the pause and sentinel; report unknown usage honestly. A separate explicit user resume permits only the named remaining step. No duplicate writer or automatic retry. |

Testable hypothesis: complete check receipts and focused first reads reduce repeat
tool execution and rereading during long tasks while preserving result quality,
required checks and stop boundaries. Compare the same held-out dependent task
with equal capabilities and authority; measure accepted completion, receipt
reuse, justified rereads and full task-family accounting before cost/time. The
Codex compaction regression is an offline prerequisite for such a comparison,
not evidence that the hypothesis succeeds. The current $2 target/$3 ceiling gate
remains unresolved. New paid trials need their own approved design/allocation.

## Validation

All 87 repository tests passed in 3.395 seconds, including the five new regression
methods. The earlier focused correction pass ran 27 tests; the subsequent full
suite includes the fifth new method. Full logs are retained here as
[red.log](red.log), [focused.log](focused.log) and [suite.log](suite.log). One line
of trailing terminal whitespace was trimmed from the archived red log; test
content is unchanged. The full
suite's summary was read from its saved log; trailing fixture output did not
trigger a rerun.

Structure/protected-source validation passed: seven local links, five Codex
profiles and 74 protected native/historical files. Skill structure and instruction
health passed. Thirteen frozen source hashes, response/compaction reconciliation,
tool counts, changed Markdown links/fences and whitespace were checked. Installer
checks use temporary homes through the existing suite. The shared runner and
live routing/settings were unchanged. The previous independent Stage A acceptance
covers its historical inputs; it does not certify this later diagnostic extension.
No live capture or efficiency claim is added.

## Independent correction review and fresh preparation

The [independent review](review.json) initially requested two corrections. An
invalid earlier bool/float count could compare equal to a later integer and be
lost during deduplication; `cache_write_input_tokens` also lacked validation.
The extractor treated an empty response ledger as successful reconciliation.
These were defects in the extension at `cf4a306`, beyond its passing test scope.

Every compaction record is now validated before duplicate comparison. Invalid
status remains attached to that response ID, and cache-write counts receive
strict integer/nonnegative validation. Missing response totals and comparisons
now remain `null`; valid zero usage still reconciles. Frozen inputs were preserved
and the derived summary was regenerated. Parent measurements above are unchanged.

Two more regression methods reproduced six failure cases before correction.
The [focused check](review-focused.log) passed 30 tests; the
[full suite](review-suite.log) passed 89 tests in 4.227 seconds. The failing cases
are retained in [review-red.log](review-red.log); trailing terminal whitespace
was trimmed when archiving these three logs. Structure/protected-file, skill,
instruction and whitespace checks passed. Separate extractor checks verified
absent and valid-zero usage against temporary files and the corrected frozen
summary. The reviewer accepted both corrections with no remaining blocker in
that scope. This does not certify live qualification, permissions or savings.

[Fresh offline preparation](../test-evidence/live-preflight-2026-10-10.json)
records three scratch families for the reviewed adapter. Frozen-input checks and
the matched semantic pair passed. Claude version was 2.1.296. Prior preparations
and their historical evidence were preserved. No benchmark parent or helper
started. The budget question remains unanswered; a general continuation does not
select between reported limits with headroom and a strict pre-request cap.
