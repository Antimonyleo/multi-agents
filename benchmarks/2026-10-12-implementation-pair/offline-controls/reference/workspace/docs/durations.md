# Duration requirements

## D1: Duration values
A duration is absent or null (unknown), or an object with exactly two keys:
value and unit. The unit must be the exact string ms or s. The value must be
an int or float, excluding bool, finite and nonnegative. Zero is valid.
Normalize ms unchanged and s multiplied by 1000. Do not round or truncate.
The normalized value must be representable as a finite number; reject overflow.
Strings, missing value/unit, extra duration keys and unsupported units are invalid.

## D2: Arithmetic
All duration sums must be finite. Reject overflow as invalid input. Numeric JSON
fields may use integer or float encodings; bool is never a numeric output.
Do not replace unknown duration with zero. Unknowns have the separate rules in A3.
