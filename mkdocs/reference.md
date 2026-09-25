# Reference

## CLI Arguments

| Flag        | Default               | Description                          |
| :---------- | :-------------------- | :----------------------------------- |
| `--server`  | required              | Hostname or IP address               |
| `--port`    | required              | TCP port (`1`–`65535`)               |
| `--delay`   | `1`                   | Seconds between probes (`0` or more) |
| `--count`   | run until interrupted | Number of probes                     |
| `--timeout` | `1`                   | Socket timeout in seconds            |
| `--version` | —                     | Print the package version and exit   |

`--timeout` must be greater than `0` when set. Omit `--count` to run
until Ctrl-C.

## Exit Codes

| Code | When                                                          |
| :--- | :------------------------------------------------------------ |
| `0`  | Help, version, Ctrl-C, or every `--count` probe succeeded     |
| `1`  | Invalid arguments, or at least one `--count` probe failed     |

## Library

| Name              | Meaning                                                                   |
| :---------------- | :------------------------------------------------------------------------ |
| `probe_tcp_port`  | Open one TCP connection and time the handshake                            |
| `run_probes`      | Repeat probes; default `count` is `1`; `None` runs until stopped          |
| `ProbeResult`     | Frozen result: `ok`, `host`, `port`, `sequence`, `elapsed_ms`, `detail`   |
| `ProbeSummary`    | Frozen totals: `total`, `passed`, `failed`, `fail_percent`, `results`     |
| `DEFAULT_DELAY`   | Default inter-probe delay (`1`)                                           |
| `DEFAULT_TIMEOUT` | Default socket timeout (`1`)                                              |
| `get_version()`   | Return the package version string                                         |

`probe_tcp_port` never raises for a refused port, a timeout, or a
socket error. Those come back as `ok=False` with a lowercase
`detail`. The CLI maps those strings to the original ping-style
wording. Host values are stripped. `ValueError` is raised for an
empty host, a bad port, a non-positive timeout, a negative delay, or
a `count` that is not greater than `0`. `run_probes` defaults to one
probe; pass `count=None` to run until `should_stop` or forever.
