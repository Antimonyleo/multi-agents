# Native extraction calibration

Run the narrow wrapper with `prepare --provider codex|claude --arm baseline|workflow --output NEW_DIRECTORY`, then `run --output DIRECTORY`. Preparation freezes prompt, truth, source, installed configuration, agent hashes and synthetic files. Run refuses an existing trace/execution receipt. The existing workflow-evaluation timeout runner is imported; no new orchestrator is installed.

The fixture has 96 JSON documents. The task selects the latest enabled ready record in each document, ignoring newer pending, disabled and case-mismatched records. An independently written raw-input algorithm checks generator truth; tests exercise incomplete, duplicated, unsorted, wrong and incorrectly typed answers. Ground truth is outside the task workspace.

User settings and native role definitions stay unchanged. Both arms use the same main model and effort within a runtime. Runtime overrides disable unused resources and restrict this synthetic task. Permissions are not equivalent across runtimes; compare only within a runtime. The baseline explicitly declines skills/delegates; the workflow snapshots the current shared skill and permits zero or one native explorer. User/global catalog context may still be present in both arms. This evaluates explicit workflow use, not a clean-machine absence of the installed skill.

Native Codex transcripts are selected through the exact scratch cwd plus parent identity. Claude transcripts are selected by the generated session UUID. Raw usage is preserved. Cumulative Codex usage snapshots use the last recorded total, not their sum. Parent/child inclusion semantics remain unknown when delegation occurs; no automatic net-cost claim is issued. Missing usage is not zero. Runtime telemetry does not prove server-side model identity.

The initial pilot has four starts and at most two optional support calls. Each session has a 300-second process-group deadline. Claude requests its supported $2 CLI limit; Codex has no hard dollar cap here. Start caps and support restrictions are declared, not a complete model scheduler. Do not launch a further trial to fill metadata or retry unchanged failure. A timeout receipt proves the owned CLI/process-group cleanup attempt, not universal external-child termination.

This wrapper currently depends on the existing host harness path recorded in `manifest.json`. Offline tests need no model calls. Project2 remains paused; these fixtures contain no scientific data or jobs.
