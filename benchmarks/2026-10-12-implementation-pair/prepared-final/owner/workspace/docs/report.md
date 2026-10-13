# Report requirements

## R1: Stable report
The result has exactly jobs and totals keys. jobs is an array sorted by job using
Python string ordering. Each job row has exactly job, attempts, last_attempt,
state, duration_ms, known_duration_ms and unknown_attempts. state uses the final
attempt status, with the same success/failed/stopped enum.
Totals has exactly jobs, successful_jobs, failed_jobs, stopped_jobs,
known_duration_ms, duration_ms and unknown_attempts. jobs counts job rows.
State counts count JOBS, not attempts. known_duration_ms sums known durations
across all attempts. unknown_attempts sums job unknown counts. duration_ms is
null if any attempt is unknown; otherwise it is the full known sum. An empty
batch has an empty jobs array and every total numeric field equal to zero.
Retain unrounded milliseconds. Numeric fields must be finite, never bool.

## R2: Invalid input
If ANY record, duration, duplicate identity, payload shape or sum is invalid,
report.generate returns exactly {"error":"invalid_input"}. Do not silently
skip malformed records or return partial jobs. A missing attempts key or a
non-list attempts value is invalid. Use ValueError between internal modules.
