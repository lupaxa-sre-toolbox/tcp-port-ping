<p align="center">
  <a href="https://github.com/lupaxa-sre-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/sre-toolbox/readme-logo.png" alt="SRE Toolbox" />
  </a>
</p>

<h1 align="center">TCP Port Ping</h1>

Repeatedly connect to a TCP host and port and report latency.

Requires Python 3.13 or newer. The runtime is the standard library
only.

## Install

```bash
pip install lupaxa-tcp-port-ping
tcp-port-ping --help
```

## CLI

```bash
tcp-port-ping --server example.com --port 80
tcp-port-ping -s example.com -p 443 -d 1
tcp-port-ping -s 192.0.2.10 -p 22 --count 5 --timeout 0.5
python -m lupaxa.tcp_port_ping --version
```

The tool opens a TCP connection, times the handshake, closes it, and
repeats after `--delay` seconds (default `1`). `--server` and `--port`
are required. `--timeout` bounds the socket (default `1` second). Omit
`--count` to run until Ctrl-C. A successful probe prints
`Connected to <host>[<port>]: tcp_seq=<n> time=<ms> ms`. Timeouts
print `Connection timed out!`. A refused port prints
`Port is closed!!!`. The summary is
`TCP Ping Results: Connections (Total/Pass/Fail): [T/P/F] (Failed: N%)`.
Ctrl-C prints that summary immediately and exits `0`.

### Flags

| Flag        | Default               | Description                                |
| :---------- | :-------------------- | :----------------------------------------- |
| `--server`  | required              | Hostname or IP address (`-s`)              |
| `--port`    | required              | TCP port (`1`–`65535`, `-p`)               |
| `--delay`   | `1`                   | Seconds between probes (`0` or more, `-d`) |
| `--count`   | run until interrupted | Number of probes (`-c`)                    |
| `--timeout` | `1`                   | Socket timeout in seconds (`-T`)           |
| `--version` | —                     | Print the package version and exit         |

`--timeout` must be greater than `0`. `--count` must be greater than
`0` when set.

### Exit Codes

| Code | When                                                          |
| :--- | :------------------------------------------------------------ |
| `0`  | Help, version, Ctrl-C, or every `--count` probe succeeded     |
| `1`  | Invalid arguments, or at least one `--count` probe failed     |

### Examples

HTTPS:

```bash
tcp-port-ping --server example.com --port 443
```

Five SSH probes, half-second timeout (exit `1` if any fail):

```bash
tcp-port-ping -s 192.0.2.10 -p 22 --count 5 --timeout 0.5
```

Back-to-back local probes (`--delay 0` is valid):

```bash
tcp-port-ping -s 127.0.0.1 -p 8080 --delay 0 --count 10 --timeout 0.2
```

## Library

```python
from lupaxa.tcp_port_ping import probe_tcp_port, run_probes

one = probe_tcp_port("example.com", 443, timeout=1.0)
print(one.ok, one.elapsed_ms, one.detail)

summary = run_probes("example.com", 443, count=3, delay=0)
print(summary.total, summary.passed, summary.failed, summary.fail_percent)
```

`probe_tcp_port` returns a `ProbeResult` with `ok`, `host`, `port`,
`sequence`, `elapsed_ms`, and `detail`. Host whitespace is stripped.
`detail` is a short lowercase reason (`connected`,
`connection timed out`, `port is closed`, or `OS error: …`). The CLI
maps those strings to the ping-style wording above. Refused ports,
timeouts, and socket errors return `ok=False` instead of raising.

`run_probes` returns a `ProbeSummary` (`total`, `passed`, `failed`,
`fail_percent`, `results`) and defaults to one probe. Pass
`count=None` to run until `should_stop` or forever. Invalid `host`,
`port`, `timeout`, `delay`, or `count` raises `ValueError`.

## Development

```bash
make init
make python-install-dev
make python-check
```

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
