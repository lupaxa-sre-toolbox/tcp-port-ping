# Examples

## HTTP probe

```bash
tcp-port-ping --server example.com --port 80
```

1 second delay, 1 second timeout. Press Ctrl-C for the summary.

## HTTPS on port 443

```bash
tcp-port-ping --server example.com --port 443
```

## Finite SSH check

```bash
tcp-port-ping -s 192.0.2.10 -p 22 --count 5 --timeout 0.5
```

Exits `0` if all five connects succeed, or `1` if any fail.

## Fast local loop

```bash
tcp-port-ping -s 127.0.0.1 -p 8080 --delay 0 --count 10 --timeout 0.2
```

`--delay 0` is valid when you want probes back to back.

## Library

```python
from lupaxa.tcp_port_ping import probe_tcp_port, run_probes

one = probe_tcp_port("example.com", 443, timeout=0.5)
print(one.ok, f"{one.elapsed_ms:.2f} ms", one.detail)

summary = run_probes("example.com", 443, count=5, delay=0.25)
print(summary.total, summary.passed, summary.failed, f"{summary.fail_percent:.2f}%")
```
