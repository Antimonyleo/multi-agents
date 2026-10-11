# Transport configuration contract
CLI options override nonempty environment values, then deployment defaults.
Retries must be an integer from 0 through 5; zero disables retries.
Timeouts must be integers from 10 through 500 milliseconds.
The local client accepts seconds. The remote client accepts milliseconds.
Both drivers must preserve the configured timeout duration.
Invalid configuration fails before calling a driver. JSON output uses null
for unavailable retry, configuration-timeout and client-timeout fields.
