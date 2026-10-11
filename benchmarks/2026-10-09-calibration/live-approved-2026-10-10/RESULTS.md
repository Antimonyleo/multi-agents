# Approved qualification result

The qualification is terminal but unaccepted for comparison. Capture, exact
output and cleanup passed; the fixture omitted the required denied-operation
probe. Independent review supports stopping. Neither comparison arm started.

Authority, limits and counters are in [allocation.json](allocation.json).
The user approved reported native caps and possible overshoot; the $3 nominal
ceiling is not a strict aggregate bound. Source checkpoint: `05c6748`.
Claude CLI at preflight: `2.1.296`. One parent and one helper ran, with no retry.

| Observation | Result |
| --- | --- |
| Wall time | 13.078 seconds |
| Opus parent model estimate | $0.1998914 |
| Haiku helper model estimate | $0.0013458950000000002 |
| CLI family estimate | $0.201237295 |
| Comparison starts | 0 of 2 prepared arms |
| Denied-operation probes | 0 |

The native trace links one `scientific_explorer` to a Haiku child at high
effort. Its two distinct message IDs reconcile with CLI input/cache/output
counters. Model estimates sum to the tree-wide CLI estimate within floating
point precision. Child usage is already included; adding it again would double
count. Actual billing and external review/coordinator cost are unknown.

The owned process group ended with no remaining live or zombie members and no
cleanup signals. This establishes owned-group cleanup only; escaped/external
children are outside the observation. All seven capture/output/boundary checks
passed. A successful allowed read, `dontAsk` mode and an unchanged workspace
do not prove denial enforcement. This is missing evidence, not an observed
permission bypass.

Evidence: [preflight](preflight.json),
[qualification assessment and five frozen hashes](qualification-assessment.json),
[metrics](qualification/metrics.json), [execution](qualification/execution.json),
[independent review](review.json) and [validation](validation.json).
The trace and copied native transcript remain beside these files. Frozen
preparations are host-specific evidence; preflight does not authorize reuse.
Project2 remains paused. No scientific, savings or default-policy claim follows.

## Next permission-test design (offline only)

Prepare one harmless denied command, exactly
`printf WORKFLOW_PERMISSION_PROBE`, with a scoped rule
`Bash(printf WORKFLOW_PERMISSION_PROBE)`. Keep Bash exposed so an actual
attempt can produce denial evidence. The documentation distinguishes scoped
rules from a bare tool denial, which removes the tool from context; deny rules
take precedence over allow rules. This proposed test follows that documented
behavior and has not run. [Permissions documentation](https://code.claude.com/docs/en/permissions).

Freeze launch-only settings through `--settings`, which supports a JSON file
or inline JSON for the session. Preserve existing native/global settings and
hook controls. [CLI reference](https://code.claude.com/docs/en/cli-reference).
Use an allowed fixture Read plus the exact denied Bash attempt in the parent;
keep the native read-only helper's task and tools intact. Match resulting
controls in any future comparison preparations. Command substitution, shell
wrappers and altered commands are outside this probe.

Implement the check in the existing adapter. Require correlated tool-call and
runtime-denial evidence for that exact command, plus the successful allowed
read, expected helper identity/accounting and verified cleanup. A model's
statement that access was denied does not count. An absent attempt, unrelated
tool error or unsupported denial shape leaves enforcement unknown. Unexpected
successful command execution fails the gate. The command only prints a marker
if enforcement is absent; it does not modify files.

Validate offline with fixtures for exact denial, no call, altered command,
unrelated error, malformed capture and unexpected success. Freeze settings and
prompt into the existing manifest checks; retain the usual source drift guard.
One exact rule test supports that rule's enforcement only, not general file or
OS isolation. Parent and helper capabilities remain separate claims.

This is a concrete design, not an implemented probe or new launch authority.
Complete its narrow offline checks and local checkpoint before requesting a
separately scoped qualification start. The current comparison slots and reserve
do not authorize qualification retries.
