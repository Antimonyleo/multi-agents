# Continuity kit audit — 2026-10-16

The kit provides a useful, small recovery mechanism. It is **not ready for broad
activation**, and this audit does not establish that long-session drift or early
stopping is solved. The candidate is committed separately at `c298775` on
`continuity-v2-20261016`. The live skill remains at its `c20214a` source version.
No remote push, global hook installation or real scientific work was performed.

## Accepted implementation

The candidate adds one recovery script, an on-demand long-task reference, a short
entrypoint pointer, 47 recovery regressions and the kit's MIT attribution. It
reuses the existing plan's Execution contract and rolling Current work/Boundaries
sections. A digest pins the contract; progress can change without repinning it.
Recovery delivers complete selected source sections within 4,096 UTF-8 bytes or
reports an unverified handoff. Matching source is neither scientific validation
nor permission to override a pause. Native goals handle continuation; a plan file
alone cannot keep a runtime executing.

The entrypoint grows by 359 bytes. The conditional reference is 4,092 bytes;
the script is 10,059 bytes and is not injected as instructions. These are byte
counts, not token or cost measurements.

Independent review found a parser defect: an invalid backtick fence could hide a
real pause and select stale text. The candidate now follows the relevant
CommonMark fence rule, with a regression. The original probe failed; the fixed
recovery lane passed 11/11 checks. Audit-only instructions also distinguish an
authorized scope amendment from the original fixed-contract numeric grade.

No second planner, permanent review team, custom Stop loop, wake service, job
manager or per-tool review was installed. The optional job wrapper stays excluded:
a reproduced timeout case can leave a SIGTERM-ignoring child alive after its
parent exits. An owned-child kill was attempted in the disposable execution
sandbox; post-signal liveness was not retained, so cleanup is not certified.
The v1 migration instructions were read; no active v1 path/binding was found in
the inspected installation, and none was replaced.

## Independent review

These were real native `scientific_reviewer` agents, each started without inherited
conversation, using `gpt-6-astra/high` verified in native metadata. Filesystem
separation was procedural, not an enforced read-only sandbox. The owner ran
mutating probes separately; the adjudicator independently checked material fixes.

| Review | Actual agent/session ID |
| --- | --- |
| Recovery | `01a14716-0f39-7fd2-9152-5d2feef025fe` |
| Lifecycle | `01a14716-26e4-7c42-b02a-0db48d11a728` |
| Science/minimality | `01a1471a-0564-77e0-a43a-9c1ad3bba2d0` |
| Separate adjudication | `01a1471c-f5a4-7760-be7a-99f31e637b39` |

An earlier science reviewer (`01a14716-400e-7f33-8ebe-ce2c750a5fdd`) received an
owner test summary before sealing its report. It was excluded and retained; one
fresh replacement supplied the accepted independent review. This was an isolation
correction, not a retry selected for a favorable verdict.

Final adjudication qualifies the minimal core only for the observed fixed-scope
native behaviors and finds insufficient evidence for broad activation. Its sealed
report and independently verified evidence are retained in
`out/continuity-v2-audit/reviews/adjudicator/output/final-{adjudication,evidence}.json`.

## Offline checks

| Check | Final result |
| --- | --- |
| Original supplied kit | 106/106 tests passed, exit 0 |
| Original repository | 182/182 tests passed, exit 0 |
| Adapted kit, serial | 107/107 tests passed, exit 0 |
| Candidate repository | 229/229 tests passed, exit 0 |
| Repository validator, skill structure checker, instruction health | Each exit 0 |
| Temporary-home install, installed check, receipt rollback | Each exit 0; 12 destinations restored |
| Saved-state replay | 128/128 cycles, 32 fresh Python processes; changed source rejected |
| Selected mutations | 6/6 detected; not exhaustive |

The concurrent adapted-kit run failed one excluded-wrapper timing assertion
(4.8726 seconds against a 4-second threshold). Its log remains; a justified serial
recheck passed without changing the threshold. An installer uninstall attempt
refused copied Codex profiles, exit 1; the documented receipt rollback then
restored all 12 temporary destinations. Global homes were not installer targets.
Local Python was 3.11.2. Replay used no model calls or native compactions.

Required candidate commands were:

```sh
python scripts/validate.py
python -m unittest discover -s tests -v
/usr/bin/python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skill/scientific-workflow
agent-workflow check --repo .
```

## Real native pilot

Both arms used the existing workflow and native goal support; the treatment added
the recovery extension. The disposable task compared train-only constant and
affine fits against frozen `2*x`, with 24 training and 16 test rows, conversion
from milliseconds to seconds, a four-fit ceiling and four planned milestones.
This was one functional pair per runtime, not a performance benchmark.

| Runtime/arm | Native session ID | Observed lifecycle |
| --- | --- | --- |
| Codex baseline A | `01a1471f-d71e-7380-820e-32a08b0b936e` | Goal complete; 3 manual compactions; resume; pause retained |
| Codex extension B | `01a14722-64d7-7083-b46f-1250276d2987` | Goal complete; 3 manual compactions; resume; pause retained |
| Codex B fresh reconstruction | `01a1472d-320a-75a3-9f09-2f6ea02927d7` | New session recovered question, units, negative result, budget and unknown job |
| Corrected Claude baseline A | `1e129e1a-d7e4-4eac-be31-78779036ea91` | Goal met; 1 manual compaction |
| Corrected Claude extension B | `f549b810-a88b-4a9b-97a2-bdef4904c2e4` | Goal met; 1 manual compaction; process resume; pause retained |

All four valid initial arms reached all four milestones without a user "continue"
message. Independent adjudication reproduced all 192 saved predictions and found
the task/data hashes unchanged. Each arm used two fits. The common negative
result was preserved: baseline test MAE was 0 seconds, constant approximately
1.00538 seconds and affine approximately 0.0846943 seconds, each over 16 test rows.
There was no evidence that the extension caused better completion: the baselines
also completed. Goal completion and numeric correctness did not establish full
scientific acceptance.

Native Codex was 0.162.1 (`gpt-6.1-sol/high`); the owner/reviewer host recorded
0.163.0. Claude was pinned to its initial 2.1.296 (`Opus 5.5/high`) for the corrected
pair. Its native updater changed the global executable link to 2.1.302 during the
audit without an owner update command; that version is not qualified here.
Actual native APIs/interactive commands were used, not slash-command prose or
synthetic replay. Relevant host documentation: [Codex hooks](https://learn.chatgpt.com/docs/hooks),
[Codex app-server](https://learn.chatgpt.com/docs/app-server),
[Codex goals](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex)
and [Claude hooks](https://code.claude.com/docs/en/hooks).

Delivered treatment contexts were complete source sections: Codex startup 1,301
bytes, later injections 2,610–2,755 bytes; corrected Claude startup 1,301 bytes and
compact 2,703 bytes. All stayed below 4,096 bytes. Claude process resume preserved
source facts, but separate `SessionStart:resume` hook delivery was not observed.
All observed compactions happened **after** the scientific milestones completed.
There was no automatic compaction or productive unfinished-task compaction test.
The unknown-job record was an injected unresolved-state marker, not a running job;
pause retention was explicitly prompted, not measured as spontaneous detection.

### Failures and unresolved gates

- The original Claude pair was invalid: `claude-mem@thedotmack` injected baseline
  results and a COMPLETE checkpoint into treatment startup. Original A session
  `328facc7-5098-4f82-8366-3102e5fab803` and the unstarted B record are retained.
  One corrected pair disabled that plugin for those invocations only. Global
  memory settings/data were left alone. This demonstrates contamination in this
  pilot, not the cause of every earlier context failure.
- Corrected Claude A's report and checkpoint falsely say all test inputs lie in
  the training range. One of 16 test rows is below it: test minimum 0.0625 versus
  training minimum 0.0833333. Passing numeric checks did not catch this claim.
- Corrected Claude B wrote a contract record labelled "Superseded/Not active"
  before its authorized amendment succeeded. The active plan stayed unchanged.
  This invalid intermediate record remains evidence; the final response correctly
  disclosed the block. A replacement must be verified before retiring its source.
- Claude B's negative control used its session scratchpad beyond the literal
  worker-only wording. Available sanitized traces do not establish the precedence
  of runtime scratch instructions, so authority compliance is uncertain. Inspection
  found no oracle/sibling reads. Scratch verification did not refit; the attempted
  second fit invocation refused before loading inputs, supporting two actual fits.
- The scope-change probe first hit an external 180-second timeout before edits.
  That is an interrupted invocation, not an agent choosing to stop. A bounded
  continuation within the original episode allowance then hit native approval
  denials: the read-only digest command was labelled `Security Weaken`; the
  four-to-five ceiling edit was labelled `Instruction Poisoning`. No blocked edit,
  digest/rebinding or approval-policy change was performed through another route.
  The four-fit ceiling, user pause, negative result and unknown job remain intact.

Further qualification would need a separately bounded, useful **unfinished** task
through native compaction; automatic compaction if claimed; verified Claude resume
hook delivery/current CLI compatibility; and a permitted transactional scope-change
test. Default memory-enabled isolation also remains unqualified. No additional
model sessions were launched to erase failures or manufacture those observations.
An inconclusive scientific outcome, substantive method-choice intervention and
trivial-task overhead were not exercised. Treatment-only recovery probes are
functional observations, not matched evidence of an improvement.
Exposed usage/action records are saved, but complete owner/reviewer/plugin/native
overhead is unknown. No token savings, causal latency gain or multi-hour reliability
claim follows from this pilot.

## Decision, evidence and rollback

Keep the three-file recovery surface as a staged candidate. Do not broadly install
it yet. The next engineering priorities are deterministic checks for consequential
report claims, safe contract replacement, and isolation of stale memory from active
authority. More standing reviewers or longer rules would not remove these defects.
The recovery script restores written state; it cannot correct false or missing state.

Local retained evidence is under `out/continuity-v2-audit/` (index, adapted kit,
review reports, full check logs/exit receipts and sanitized native events) and
`out/continuity-v2-pilot/` (inputs, outputs, frozen graders, scope intervention,
usage summaries and retirement receipt). These directories are Git-ignored and
are **not included in this documentation commit or available from a fresh clone**.
The original uploaded ZIP is preserved. Its SHA-256 is
`abe55cd3b7dfad796d5a107ec07ad03a7676f3f1ae4cdc8e15050ac736d55290`;
the final kit's selected-file digest is
`b0942d208de2992cb90b18c52867877406a189b9b1b50f11ed9afdd364a8d506`.
This digest covers the audit tool's selected files, not the whole repository.

The isolated source worktree is
`/home/hao/.cache/codex-scratch/continuity-v2.dby2dhwe/upstream`.
Pilot hooks were retired by renaming only their project-local settings to retained
inactive files. Owned native pilot processes exited; Codex goals were paused and
Claude comparison goals were met. Shared services and other jobs were preserved.
There is no live source rollback to perform. Leave the candidate branch unmerged;
if later activated, revert its commit to restore the source and retire only bindings
owned by that deployment. Keep the stable script path until its last binding is
retired; do not delete active callback targets or overwrite unrelated settings.

Use the [reusable long-task prompt](long-task-prompt.md) with the current workflow.
It states completion, authority, scientific evidence and stop boundaries without
requiring the recovery candidate or a new planner.
