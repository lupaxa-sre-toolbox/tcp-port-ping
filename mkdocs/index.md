# TCP Port Ping

`lupaxa-tcp-port-ping` opens a TCP connection to a host and port, times
the handshake, and repeats so you can see whether the service is
reachable.

Install the package for the library API and the `tcp-port-ping`
console command:

```bash
pip install lupaxa-tcp-port-ping
tcp-port-ping --server example.com --port 443
```

You can also run `python -m lupaxa.tcp_port_ping`.

## What it Does

- Connects to the host and port you name
- Times the TCP handshake in milliseconds
- Repeats after `--delay` seconds (default `1`)
- Requires `--server` and `--port`, with a 1 second socket timeout by default
- Runs until Ctrl-C unless you pass `--count`
- Prints total, pass, fail, and the failure percentage
- Exposes `probe_tcp_port` and `run_probes` as library functions
