# Bounded historical-session review

Frozen selection before decision-excerpt inspection, 2026-10-10.

Question: which observed long-session failures or repeated work should the next
workflow tests cover? This review does not estimate counterfactual savings.

Use the two parent transcripts in [sample.json](sample.json). Metadata inspection
found one long Claude workflow-repository session and one long Codex parent in a
scientific repository. Excerpt inspection identified JAX research and migration
preparation in that Codex session; the frozen selection was retained. Select
the largest qualifying transcript per runtime from the inspected 2026-10-09
parents, without selecting for outcome. Exclude the short transfer/setup controls.
This convenience sample covers workflow maintenance and scientific preparation,
not representative scientific execution. Inspect completion and failure/recovery episodes within it;
do not label an entire multi-request session a scientific success or failure.

Freeze paths, byte lengths and SHA-256 before extraction. Codex child discovery is
limited to verified descendants in the same daily directory. Inspect Claude's
matching subagents directory. Absence in these locations is not proof that no
child existed elsewhere. Do not add child totals to parent totals without verified
inclusion semantics. Source drift stops extraction instead of changing the sample.

Use one offline script for record and tool counts. Deduplicate native response IDs
for usage and tool IDs for actions. Keep input, cached input and output separate.
Codex cached tokens are a subset of input; Claude cache creation/read counts are
separate input categories. Do not compare raw totals across providers as cost.
Report observed task durations and explicit wait calls; neither is pure reasoning
time. User gaps, tool latency and unobserved waiting remain separate or unknown.

Inspect only user requests, final answers, repeated command candidates and nearby
decision excerpts. Track compactions, errors, required checks, checkpoint claims,
drift and recovery. Repeated commands may be justified by source changes, red/green
regressions or required gates; repetition alone is not waste. Preserve line numbers
and bounded excerpts for findings. Do not export full transcripts or credentials.

Deliverable: a short evidence-backed report, reproducible count script/summary,
and concrete behavioral test specifications added to the existing test plan.
Specifications remain unexecuted. No model-backed benchmark, runtime setting,
native agent, live skill routing or scientific objective changes are authorized.
Project2 remains paused; the $2 target/$3 ceiling interpretation stays unresolved.

Scope amendment after extraction: the Codex cumulative snapshot omits exactly
three recorded compaction responses. Add separate native record/compaction
telemetry to the existing adapter and regression tests. Preserve provider totals
and all claim/launch gates. This is capture evidence, not a billing correction.

Completion: verify hashes and count reconciliation; inspect findings against their
source lines; check changed Markdown links/fences/whitespace, repository structure,
the required unittest suite, skill structure and instruction health. Checkpoint
this scoped work locally. No push.
