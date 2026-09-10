"""Command-line interface for TCP Port Ping."""

from __future__ import annotations

import argparse
import math
import signal
from types import FrameType

from .probe import (
    DEFAULT_DELAY,
    DEFAULT_TIMEOUT,
    DETAIL_OS_ERROR_PREFIX,
    DETAIL_REFUSED,
    DETAIL_TIMEOUT,
    ProbeResult,
    ProbeSummary,
    run_probes,
    summarize,
)
from .version import get_version


def _positive_timeout(value: str) -> float:
    try:
        timeout = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("timeout must be a number") from exc
    if not math.isfinite(timeout) or timeout <= 0:
        raise argparse.ArgumentTypeError("timeout must be greater than 0")
    return timeout


def _non_negative_delay(value: str) -> float:
    try:
        delay = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("delay must be a number") from exc
    if not math.isfinite(delay) or delay < 0:
        raise argparse.ArgumentTypeError("delay must be 0 or greater")
    return delay


def _tcp_port(value: str) -> int:
    try:
        port = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("port must be an integer") from exc
    if port < 1 or port > 65535:
        raise argparse.ArgumentTypeError("port must be between 1 and 65535")
    return port


def _positive_count(value: str) -> int:
    try:
        count = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("count must be an integer") from exc
    if count < 1:
        raise argparse.ArgumentTypeError("count must be greater than 0")
    return count


def _exit_code(exc: SystemExit) -> int:
    code = exc.code
    if code is None:
        return 0
    return code if isinstance(code, int) else 1


def build_parser() -> argparse.ArgumentParser:
    """Build the ``tcp-port-ping`` argument parser."""
    parser = argparse.ArgumentParser(
        description="Repeatedly connect to a TCP host and port and report latency.",
    )
    parser.add_argument(
        "-s",
        "--server",
        required=True,
        metavar="HOST",
        help="Hostname or IP address",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=_tcp_port,
        required=True,
        metavar="PORT",
        help="TCP port",
    )
    parser.add_argument(
        "-d",
        "--delay",
        type=_non_negative_delay,
        default=DEFAULT_DELAY,
        metavar="SECONDS",
        help=f"Delay between probes in seconds (default: {DEFAULT_DELAY:g})",
    )
    parser.add_argument(
        "-c",
        "--count",
        type=_positive_count,
        default=None,
        metavar="N",
        help="Number of probes (default: run until interrupted)",
    )
    parser.add_argument(
        "-T",
        "--timeout",
        type=_positive_timeout,
        default=DEFAULT_TIMEOUT,
        metavar="SECONDS",
        help=f"Socket timeout in seconds (default: {DEFAULT_TIMEOUT:g})",
    )
    parser.add_argument("--version", action="version", version=get_version())
    return parser


def format_probe_line(result: ProbeResult) -> str:
    """Return the per-probe line printed by the CLI."""
    if result.ok:
        elapsed = f"{result.elapsed_ms:.2f}"
        return (
            f"Connected to {result.host}[{result.port}]: "
            f"tcp_seq={result.sequence} time={elapsed} ms"
        )
    if result.detail == DETAIL_TIMEOUT:
        return "Connection timed out!"
    if result.detail == DETAIL_REFUSED:
        return "Port is closed!!!"
    if result.detail.startswith(DETAIL_OS_ERROR_PREFIX):
        return f"OS Error: {result.detail[len(DETAIL_OS_ERROR_PREFIX) :]}"
    return result.detail


def format_summary(summary: ProbeSummary) -> str:
    """Return the Ctrl-C / end-of-run results block."""
    failed = f"{summary.fail_percent:.2f}"
    return (
        "\nTCP Ping Results: Connections (Total/Pass/Fail): "
        f"[{summary.total}/{summary.passed}/{summary.failed}] "
        f"(Failed: {failed}%)"
    )


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return _exit_code(exc)

    results: list[ProbeResult] = []

    def _on_result(result: ProbeResult) -> None:
        results.append(result)
        print(format_probe_line(result))

    def _on_interrupt(_signum: int, _frame: FrameType | None) -> None:
        print(format_summary(summarize(results)))
        raise SystemExit(0)

    previous = signal.signal(signal.SIGINT, _on_interrupt)
    try:
        summary = run_probes(
            args.server,
            args.port,
            delay=args.delay,
            timeout=args.timeout,
            count=args.count,
            on_result=_on_result,
        )
    except SystemExit as exc:
        return _exit_code(exc)
    finally:
        signal.signal(signal.SIGINT, previous)

    print(format_summary(summary))
    return 0 if summary.failed == 0 else 1
