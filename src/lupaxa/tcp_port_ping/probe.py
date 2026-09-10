"""TCP connect probe: one handshake, timed like a ping."""

from __future__ import annotations

import contextlib
import math
import socket
import time
from collections.abc import Callable
from dataclasses import dataclass
from timeit import default_timer as timer

DEFAULT_DELAY = 1.0
DEFAULT_TIMEOUT = 1.0

DETAIL_CONNECTED = "connected"
DETAIL_TIMEOUT = "connection timed out"
DETAIL_REFUSED = "port is closed"
DETAIL_OS_ERROR_PREFIX = "OS error: "


@dataclass(frozen=True)
class ProbeResult:
    """Outcome of one TCP connect attempt."""

    ok: bool
    host: str
    port: int
    sequence: int
    elapsed_ms: float
    detail: str


@dataclass(frozen=True)
class ProbeSummary:
    """Aggregate of one or more TCP connect attempts."""

    total: int
    passed: int
    failed: int
    fail_percent: float
    results: tuple[ProbeResult, ...]


def _require_port(port: int) -> int:
    if port < 1 or port > 65535:
        raise ValueError("port must be between 1 and 65535")
    return port


def _require_timeout(timeout: float) -> float:
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be greater than 0")
    return timeout


def _require_delay(delay: float) -> float:
    if not math.isfinite(delay) or delay < 0:
        raise ValueError("delay must be 0 or greater")
    return delay


def _require_count(count: int | None) -> int | None:
    if count is None:
        return None
    if count < 1:
        raise ValueError("count must be greater than 0")
    return count


def _require_host(host: str) -> str:
    host = host.strip()
    if not host:
        raise ValueError("host must not be empty")
    return host


def summarize(results: list[ProbeResult] | tuple[ProbeResult, ...]) -> ProbeSummary:
    """Build a summary from collected probe results."""
    collected = tuple(results)
    total = len(collected)
    passed = sum(1 for item in collected if item.ok)
    failed = total - passed
    fail_percent = 0.0 if total == 0 else failed / total * 100
    return ProbeSummary(
        total=total,
        passed=passed,
        failed=failed,
        fail_percent=fail_percent,
        results=collected,
    )


def probe_tcp_port(
    host: str,
    port: int,
    *,
    timeout: float = DEFAULT_TIMEOUT,
    sequence: int = 0,
) -> ProbeResult:
    """Open one TCP connection and time the handshake.

    Parameters
    ----------
    host
        Hostname or IPv4/IPv6 address. Leading and trailing whitespace
        is stripped.
    port
        TCP port (``1``–``65535``).
    timeout
        Socket timeout in seconds. Must be greater than ``0``.
    sequence
        ``tcp_seq`` value reported for this attempt.

    Returns
    -------
    ProbeResult
        Success or failure for this single connect.

    Raises
    ------
    ValueError
        If ``host`` is empty, ``port`` is out of range, or ``timeout``
        is not greater than ``0``.
    """
    host = _require_host(host)
    port = _require_port(port)
    timeout = _require_timeout(timeout)

    started = timer()
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
    except TimeoutError:
        elapsed_ms = 1000 * (timer() - started)
        return ProbeResult(False, host, port, sequence, elapsed_ms, DETAIL_TIMEOUT)
    except ConnectionRefusedError:
        elapsed_ms = 1000 * (timer() - started)
        return ProbeResult(False, host, port, sequence, elapsed_ms, DETAIL_REFUSED)
    except OSError as exc:
        elapsed_ms = 1000 * (timer() - started)
        return ProbeResult(
            False,
            host,
            port,
            sequence,
            elapsed_ms,
            f"{DETAIL_OS_ERROR_PREFIX}{exc}",
        )

    with sock, contextlib.suppress(OSError):
        sock.shutdown(socket.SHUT_RD)

    elapsed_ms = 1000 * (timer() - started)
    return ProbeResult(True, host, port, sequence, elapsed_ms, DETAIL_CONNECTED)


def run_probes(
    host: str,
    port: int,
    *,
    delay: float = DEFAULT_DELAY,
    timeout: float = DEFAULT_TIMEOUT,
    count: int | None = 1,
    on_result: Callable[[ProbeResult], None] | None = None,
    should_stop: Callable[[], bool] | None = None,
) -> ProbeSummary:
    """Probe a TCP port once, ``count`` times, or until stopped.

    Parameters
    ----------
    host
        Hostname or IPv4/IPv6 address.
    port
        TCP port (``1``–``65535``).
    delay
        Seconds to wait between probes. Must be ``0`` or greater.
    timeout
        Socket timeout in seconds. Must be greater than ``0``.
    count
        Number of probes. Defaults to ``1``. ``None`` means run until
        ``should_stop`` returns true, or forever if it is omitted.
    on_result
        Optional callback invoked after each probe.
    should_stop
        Optional predicate checked before each probe and before each
        inter-probe sleep.

    Returns
    -------
    ProbeSummary
        Totals for every probe that ran.

    Raises
    ------
    ValueError
        If ``host``, ``port``, ``timeout``, ``delay``, or ``count`` is invalid.
    """
    host = _require_host(host)
    port = _require_port(port)
    delay = _require_delay(delay)
    timeout = _require_timeout(timeout)
    count = _require_count(count)

    results: list[ProbeResult] = []
    sequence = 0
    while count is None or sequence < count:
        if should_stop is not None and should_stop():
            break
        result = probe_tcp_port(host, port, timeout=timeout, sequence=sequence)
        results.append(result)
        if on_result is not None:
            on_result(result)
        sequence += 1
        if count is not None and sequence >= count:
            break
        if should_stop is not None and should_stop():
            break
        time.sleep(delay)
    return summarize(results)
