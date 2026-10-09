# Native pilot completion - 2026-10-09

The four authorized starts were executed. Three outputs passed exact 96-row extraction and workspace-preservation checks; one Codex workflow startup failed with service 503 before a usable usage result. No model session was retried. Project2 remains USER_PAUSED_DO_NOT_RESUME. No science ran. All native agents, models, effort defaults and global settings were preserved.

| Runtime/arm | Exact output | Wall seconds | CLI list-price cost estimate USD | Delegates |
| --- | --- | ---: | ---: | ---: |
| Codex baseline | PASS | 80.382 | unavailable | 0 |
| Codex workflow | startup service failure | 289.294 | unknown | 0 |
| Claude workflow | PASS | 38.012 | 0.347201 | 0 |
| Claude baseline | PASS | 41.973 | 0.2307956 | 0 |

Claude requested Opus/high; trace model was claude-opus-5-5. The workflow invoked Skill(scientific-workflow) once. Both arms used three Bash calls plus StructuredOutput, without optional support/review. Codex requested Sol/high; native context metadata recorded gpt-6.1-sol/high. No successful workflow intervention or Codex savings comparison was obtained. Server model identity is not independently established by these metadata.

Claude's one workflow-first pair had 50.44% higher CLI cost estimate and 9.44% shorter wall time. These are descriptive differences, not a reliable effect or an invoice. Cache creation/read counts and exploratory reads differed. This does not support a default change or small-helper savings. Three correct results out of four starts is an operational outcome; the service failure is not a model-quality failure. Its absent usage is unknown, not zero. The CLI performed internal transport reconnects; the outer harness made no extra session starts.

Both Claude traces dumped many raw JSON files before using deterministic extraction. The workflow inspected 50 files this way; the baseline attempted all 96. A small post-pilot instruction now directs explicit-rule extraction to representative schema inspection and scripted full-input scanning. It has not been evaluated in a new model run. Existing pre-pilot snapshots remain frozen; no native role/model/effort changed.

The wrapper imports the existing timeout/process-group runner. It preserves exact identities, native transcripts, raw CLI traces, requested/observed settings and strict grading. Ground truth is checked by an independently written raw-input reference plus good/bad scorer controls. A post-pilot collector correction handles SQLite's plain-string source field by following original transcript parent identities, tested with a synthetic child and unrelated thread; no live child dispatch was exercised. This correction does not re-score or retry the pilot.

Evidence: `pilot-evidence/SUMMARY.json`, the four per-arm manifests, prompts, exact truth/output, traces, terminal receipts and metrics. `used_adapter.py` is the exact pre-pilot wrapper. Full native transcripts remain at host paths with SHA-256 in `NATIVE_TRANSCRIPT_IDENTITIES.json`; committed CLI traces and normalized usage are portable. Host paths can expire; live parent-child accounting still needs validation before any delegated cost claim.

The adapter's six offline tests and the required repository checks are completion checks. Neither establishes live child role restrictions or maximum efficiency. Preparation/coordinator and the one completion review are separate calibration overhead, excluded from arm cost estimates; complete billed project cost is unavailable. The start/deadline restrictions are a declared resource envelope, not a universal scheduler or hard Codex dollar limit.

Remaining calibration questions are helper break-even, native child accounting/discovery, demanding implementation ownership, major-phase review benefit and repeatability. The next useful scientific-workflow measurement is an independently useful context-heavy task where a helper can avoid owner reads, compared against direct scripts under a new explicit budget. A Codex retry additionally needs restored service readiness. Do not automatically run these extensions, change the main model or treat this checkpoint as scientific resume authority.
