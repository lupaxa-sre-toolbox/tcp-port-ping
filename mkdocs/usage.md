# Usage

The CLI opens a TCP connection, times the handshake, closes it, and
repeats. Short flags match the original script: `-s`, `-p`, and `-d`.

## CLI flags

| Flag        | Default                    | Description                                      |
| :---------- | :------------------------- | :----------------------------------------------- |
| `--server`  | required                   | Hostname or IP address                           |
| `--port`    | required                   | TCP port                                         |
| `--delay`   | `1`                        | Seconds to wait between probes                   |
| `--count`   | run until interrupted      | Number of probes                                 |
| `--timeout` | `1`                        | Socket timeout in seconds                        |
| `--version` | —                          | Print the package version and exit               |

`--timeout` must be greater than `0`. `--delay` must be `0` or
greater. `--port` must be an integer from `1` to `65535`. `--count`
must be greater than `0` when set.

```bash
tcp-port-ping --server example.com --port 80
tcp-port-ping -s example.com -p 443 -d 1
tcp-port-ping -s 192.0.2.10 -p 22 --count 5 --timeout 0.5
tcp-port-ping --version
```

A successful probe prints
`Connected to <host>[<port>]: tcp_seq=<n> time=<ms> ms`. Failures
print a short reason. The summary line is
`TCP Ping Results: Connections (Total/Pass/Fail): [T/P/F] (Failed: N%)`.

## Library

```python
from lupaxa.tcp_port_ping import probe_tcp_port, run_probes

one = probe_tcp_port("example.com", 443, timeout=1.0)
if not one.ok:
    raise SystemExit(one.detail)

summary = run_probes("example.com", 443, count=3, delay=0.25)
print(summary.passed, summary.failed, summary.fail_percent)
```

`probe_tcp_port` returns a `ProbeResult` with `ok`, `host`, `port`,
`sequence`, `elapsed_ms`, and `detail`. Host whitespace is stripped.
`detail` is a short lowercase reason (`connected`,
`connection timed out`, `port is closed`, or `OS error: …`).
`run_probes` returns a `ProbeSummary` and defaults to one probe.
Pass `count=None` to run until `should_stop` or forever. Invalid
`host`, `port`, `timeout`, `delay`, or `count` raises `ValueError`.
