# Batch-attempt report repair

This is synthetic software maintenance. It contains no scientific inputs.
Repair durations.py, attempts.py and report.py as one dependent implementation.
Preserve other files. All requirements are in the three documents below.

## Entrypoints
- durations.normalize(duration): return milliseconds as a finite number. Unknown
  duration returns None; invalid duration raises ValueError.
- attempts.summarize(records): validate a list of attempt records and return job
  rows; invalid input raises ValueError. It calls durations.normalize.
- report.generate(payload): return the report or {"error":"invalid_input"}.
  The payload is an object with an attempts list. Additional payload keys are
  ignored. Additional attempt keys are ignored.
- python -B report.py: read one JSON payload from stdin, emit one JSON result
  and a newline. Invalid JSON emits {"error":"invalid_input"}. Exit normally.
  Imports must not consume stdin or print. Use only the Python standard library.

## Complete requirements
Read docs/durations.md, docs/attempts.md and docs/report.md. These documents are
normative, including error, unknown, zero, final-state and ordering rules.
Run python -B -m unittest discover -s tests -v and preserve the complete output
and direct exit. Passing public tests alone is not completion; external hidden
checks cover additional instances of these same documented requirements.
