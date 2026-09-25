# Getting Started

## Requirements

- Python 3.13 or newer
- A host and TCP port you are allowed to probe
- No runtime dependencies beyond the standard library

## Install

```bash
pip install lupaxa-tcp-port-ping
tcp-port-ping --help
```

Library import:

```python
from lupaxa.tcp_port_ping import probe_tcp_port, run_probes

one = probe_tcp_port("example.com", 443)
print(one.ok, one.elapsed_ms, one.detail)

summary = run_probes("example.com", 443, count=3, delay=0)
print(summary.total, summary.passed, summary.failed)
```

Module entry point:

```bash
python -m lupaxa.tcp_port_ping --version
```

### From Source (Development)

```bash
make init
make python-install-dev
tcp-port-ping --version
```

## First Run

Pass the host and port:

```bash
tcp-port-ping --server example.com --port 80
tcp-port-ping -s example.com -p 443 --count 5
```

Each successful connect prints the host, port, sequence, and time in
milliseconds. Timeouts print `Connection timed out!`. A refused port
prints `Port is closed!!!`. Ctrl-C (or the end of `--count`) prints
the totals. A finished `--count` run exits `0` when every probe
succeeded and `1` when any failed. Ctrl-C prints the summary
immediately and exits `0`.

## Makefile Helpers

```bash
make init                 # clone makefile-skills into .makefiles/
make python-install-dev   # editable install with [dev]
make python-check         # lint + type + test
make mkdocs-serve         # local docs site
```
