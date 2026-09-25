<p align="center">
  <a href="https://github.com/lupaxa-sre-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/sre-toolbox/readme-logo.png" alt="SRE Toolbox" />
  </a>
</p>

<h1 align="center">TCP Port Ping</h1>

Repeatedly connect to a TCP host and port and report latency.

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
`--count` to run until Ctrl-C; the summary then prints total, pass,
fail, and the failure percentage.

## Library

```python
from lupaxa.tcp_port_ping import probe_tcp_port, run_probes

one = probe_tcp_port("example.com", 443, timeout=1.0)
print(one.ok, one.elapsed_ms, one.detail)

summary = run_probes("example.com", 443, count=3, delay=0)
print(summary.total, summary.passed, summary.failed, summary.fail_percent)
```

## Development

```bash
make init
make python-install-dev
make python-check
make mkdocs-serve
```

## Documentation

The published guide is at
<https://tcp-port-ping.thelupaxaproject.org/>.

Site Markdown lives in `mkdocs/`.

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
