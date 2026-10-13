# Approved implementation comparison: terminal result

The approved comparison is closed after an invalid first measurement. The
support arm ended; the owner arm stopped without a start. There was no retry,
repair, changed scorer or favorable re-score. No matched cost/quality comparison
or general workflow benefit was established.

The user approved the exact new two-family allocation after preparation checkpoint
`4348991`: $1.50 CLI reported limit per family ($3 nominal total, possible
overshoot), 300 seconds each, sequential families, two mandatory reviewers and
at most one optional explorer. [Authority](authorization.json) and [closure](closure.json)
retain those limits. Unused allocation is not retry authority. Earlier failed
and stopped benchmark arms remain closed.

| Observation | Support arm | Owner arm |
| --- | --- | --- |
| Parent starts | 1 | 0; stopped |
| Optional explorers | 0 | Not started |
| Required native review | One Opus/high, completed ACCEPT | Not started |
| Public check | 4/4 tests, verified exit 0 | Not started |
| Frozen hidden checker | 63/65 probes | Not started |
| Measurement validity | Invalid | Conditional stop |
| Task acceptance | Unresolved | Not measured |
| CLI reported family cost | $0.869703600 | Not measured |
| Elapsed family time | 189.030 s | Not measured |

The two failed probes impose sorted output on `attempts.summarize`. The frozen
contract requires this function to return job rows, but sorting is specified
for the report's `jobs` array. Both observations match every expected row by
exact job identity and values; the report API and CLI sort correctly. The
[original oracle receipts](../prepared-final/support/oracle-probes.json) and
63/65 score stay unchanged. The [supplemental diagnosis](contract-scope-diagnosis.json)
is not a replacement score. Independent review found the failures do not
establish a disclosed-contract defect; their unsupported requirement invalidates
the measurement. [Continuation review](continuation-review.json) required
stopping before the owner arm. [The launch guard](owner-stop-verification.json)
refused that arm before creating a start marker.

All ten continuation evidence checks passed: complete usage, family inclusion,
native role identity and helper limits, observed scope, completed review,
final-version/hash binding, actual public-check execution, immutable task
inputs and retrieval assessment. They do not cure an invalid acceptance rule.
Only the three authorized modules changed; new workspace files are confined to
`receipts/`. The reviewer saw the final sources and saved full log/direct exit;
there was no later edit or check. Owned-group cleanup passed without signals,
remaining live processes or zombies. Escaped/external processes remain outside
that observation. Full raw traces, commands and terminal records are retained
under [the support arm](../prepared-final/support/terminal.json).

Independent accounting reconciled eight parent and two reviewer responses,
deduplicated by stable message ID, to all four terminal model counters:

| Token category | Parent | Reviewer | CLI family total |
| --- | ---: | ---: | ---: |
| Input | 16 | 4 | 20 |
| Output | 11,112 | 9,524 | 20,636 |
| Cache-read | 227,411 | 6,017 | 233,428 |
| Cache-creation | 43,561 | 12,346 | 55,907 |

[Response identities and native fragment counters](support-accounting.json)
prove the same-model reviewer was included. Adding its usage/cost again would
double count it. The $0.869703600 value is the CLI family estimate, including
owner implementation, integration and native review. Actual billing, coordinator,
external assessment and preparation cost remain unknown; complete project spend
and accepted-work savings cannot be claimed.

The owner read the small task directly and explained that an explorer would
replace no remaining retrieval. Therefore no explorer effect was measured.
Native settings were not edited or rolled back by this task. [Preservation](preservation-after-support.json)
confirms all 1,185 earlier benchmark files and frozen source identities unchanged.
Current Claude settings match the active seal. Both global settings files now
differ from the original preparation baseline: earlier Claude drift was already
recorded, and Codex drift is newly observed. Their provenance and exact field
differences are unknown. Do not claim global-settings preservation. The Codex
configuration is outside the matched Claude controls.

The reviewed 175-test preparation and required structure/skill checks are reused
for unchanged source; their full logs and bound source identities remain at
[final-validation](../final-validation/validation.json). The saved-evidence
extraction was independently checked against raw terminal artifacts and native
response records. Final closure review and a local Git checkpoint complete this
allocation; no push or scientific work is included.

Practical conclusion: keep one capable owner for dependent work, use scripts for
exact transformations, and delegate useful independent work that replaces owner
work. Retain consequential review and complete check receipts. The new lesson
is to bind every hidden check to an explicit requirement at its exact API boundary;
a correct report must not be rejected for an unspecified internal ordering.
A future revised comparison needs its own design and authority. Current evidence
does not justify changing model defaults or claiming savings/general reliability.
