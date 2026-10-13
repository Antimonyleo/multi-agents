# Attempt requirements

## A1: Attempt identity
records must be a list. Each record must be an object with job, attempt and
status. job is a string with at least one non-whitespace character; preserve
its exact identity. attempt is an integer >= 1, excluding bool. status is the
exact string success, failed or stopped. duration is optional, as specified in
D1. A duplicate (job, attempt) is invalid even when both records are identical.
Attempt numbers may have gaps. Input order is arbitrary. Empty records are valid.

## A2: Final state
Group by exact job identity. The final attempt is the largest numeric attempt
number, not the last input row. Its status alone is the job state. Earlier success
does not override a final failed or stopped attempt. attempts is the count of
actual records for that job; last_attempt is the largest attempt number.
Sum durations across ALL attempts, including failed and stopped attempts.

## A3: Unknown duration
For each job, unknown_attempts counts absent or null durations. known_duration_ms
is the sum of known durations, with zero for no known durations. duration_ms is
that sum only when unknown_attempts is zero; otherwise it is null. This includes
unknown durations on an earlier failed attempt even if the final success is known.
Zero duration is known, and does not increment unknown_attempts.
