<!-- markdownlint-disable -->
<p align="center">
  <a href="https://github.com/lupaxa-sre-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/sre-toolbox/readme-logo.png" alt="Project Logo" width="256"/><br/>
  </a>
</p>
<h3 align="center">
  The Lupaxa SRE Toolbox<br />
  Part of The Lupaxa Project
</h3>

<br />

# lupaxa-tcp-port-ping

Repeatedly connect to a TCP host and port and report latency.

## Features

- Open one TCP connection, time the handshake, and close it
- Repeat after a configurable delay (default 1 second)
- Required host and TCP port, with a 1 second socket timeout by default
- `--count` for a finite run; omit it to run until Ctrl-C
- Summary of total, pass, fail, and failure percentage
- Library API (`probe_tcp_port`, `run_probes`, `ProbeResult`)
- Fully typed, linted, formatted, and tested
- No runtime dependencies beyond the standard library

## Installation

### From PyPI

```bash
pip install lupaxa-tcp-port-ping
```

### From source (development mode)

```bash
pip install -e ".[dev]"
```

Requires Python 3.13+. No runtime dependencies.

## Library quick start

```python
from lupaxa.tcp_port_ping import probe_tcp_port, run_probes

one = probe_tcp_port("example.com", 443)
print(one.ok, one.elapsed_ms, one.detail)

summary = run_probes("example.com", 443, count=3, delay=0)
print(summary.total, summary.passed, summary.failed)
```

## CLI quick start

```bash
tcp-port-ping --help
tcp-port-ping --server example.com --port 80
tcp-port-ping -s example.com -p 443 -d 1
tcp-port-ping -s 192.0.2.10 -p 22 --count 5 --timeout 0.5
```

You can also run the CLI as a module:

```bash
python -m lupaxa.tcp_port_ping --help
python -m lupaxa.tcp_port_ping --version
```

## Documentation

Online documentation:

[Documentation](https://tcp-port-ping.thelupaxaproject.org/)

Source repository:

[GitHub](https://github.com/lupaxa-sre-toolbox/tcp-port-ping)

### Serve docs locally

From a clone of the repository:

```bash
make mkdocs-serve
```

Then open the local URL printed by MkDocs in your browser.

## Development

Clone the repository and install with Make:

```bash
make init                # first-time makefile-skills checkout
make python-install-dev  # editable install with [dev]
make python-check        # lint, type-check, and test
```

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
