"""TCP connect probe."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from lupaxa.tcp_port_ping.probe import (
    DETAIL_CONNECTED,
    DETAIL_REFUSED,
    DETAIL_TIMEOUT,
    ProbeResult,
    probe_tcp_port,
    run_probes,
    summarize,
)


def test_probe_success_shuts_down_and_closes() -> None:
    sock = MagicMock()
    sock.__enter__.return_value = sock
    with patch("lupaxa.tcp_port_ping.probe.socket.create_connection", return_value=sock):
        result = probe_tcp_port("example.com", 443, timeout=0.5, sequence=3)
    assert result.ok is True
    assert result.host == "example.com"
    assert result.port == 443
    assert result.sequence == 3
    assert result.elapsed_ms >= 0
    assert result.detail == DETAIL_CONNECTED
    sock.shutdown.assert_called_once()
    sock.__exit__.assert_called()


def test_probe_timeout() -> None:
    with patch(
        "lupaxa.tcp_port_ping.probe.socket.create_connection",
        side_effect=TimeoutError,
    ):
        result = probe_tcp_port("example.com", 80)
    assert result.ok is False
    assert result.detail == DETAIL_TIMEOUT


def test_probe_connection_refused() -> None:
    with patch(
        "lupaxa.tcp_port_ping.probe.socket.create_connection",
        side_effect=ConnectionRefusedError,
    ):
        result = probe_tcp_port("example.com", 81)
    assert result.ok is False
    assert result.detail == DETAIL_REFUSED


def test_probe_os_error() -> None:
    with patch(
        "lupaxa.tcp_port_ping.probe.socket.create_connection",
        side_effect=OSError("network is unreachable"),
    ):
        result = probe_tcp_port("example.com", 80)
    assert result.ok is False
    assert result.detail.startswith("OS error:")
    assert "unreachable" in result.detail


def test_probe_rejects_empty_host() -> None:
    with pytest.raises(ValueError, match="host"):
        probe_tcp_port("   ", 80)


def test_probe_strips_host() -> None:
    sock = MagicMock()
    with patch(
        "lupaxa.tcp_port_ping.probe.socket.create_connection",
        return_value=sock,
    ) as connect:
        result = probe_tcp_port("  example.com  ", 443)
    assert result.host == "example.com"
    connect.assert_called_once()
    assert connect.call_args.args[0] == ("example.com", 443)


def test_probe_rejects_out_of_range_port() -> None:
    with pytest.raises(ValueError, match="port"):
        probe_tcp_port("example.com", 0)


def test_probe_rejects_non_positive_timeout() -> None:
    with pytest.raises(ValueError, match="timeout"):
        probe_tcp_port("example.com", 80, timeout=0)


def test_run_probes_defaults_to_one() -> None:
    def fake_probe(
        host: str,
        port: int,
        *,
        timeout: float,
        sequence: int,
    ) -> ProbeResult:
        return ProbeResult(True, host, port, sequence, 1.25, DETAIL_CONNECTED)

    with (
        patch("lupaxa.tcp_port_ping.probe.probe_tcp_port", side_effect=fake_probe) as probe,
        patch("lupaxa.tcp_port_ping.probe.time.sleep") as sleep,
    ):
        summary = run_probes("example.com", 80)
    assert probe.call_count == 1
    sleep.assert_not_called()
    assert summary.total == 1
    assert summary.passed == 1


def test_run_probes_finite_count_does_not_sleep_after_last() -> None:
    calls: list[float] = []

    def fake_probe(
        host: str,
        port: int,
        *,
        timeout: float,
        sequence: int,
    ) -> ProbeResult:
        return ProbeResult(True, host, port, sequence, 1.25, DETAIL_CONNECTED)

    with (
        patch("lupaxa.tcp_port_ping.probe.probe_tcp_port", side_effect=fake_probe),
        patch("lupaxa.tcp_port_ping.probe.time.sleep", side_effect=calls.append),
    ):
        summary = run_probes("example.com", 80, delay=1, count=2)
    assert summary.total == 2
    assert summary.passed == 2
    assert summary.failed == 0
    assert summary.fail_percent == 0.0
    assert calls == [1]


def test_run_probes_stops_before_first_when_asked() -> None:
    def fake_probe(
        host: str,
        port: int,
        *,
        timeout: float,
        sequence: int,
    ) -> ProbeResult:
        raise AssertionError("should not probe")

    with (
        patch("lupaxa.tcp_port_ping.probe.probe_tcp_port", side_effect=fake_probe),
        patch("lupaxa.tcp_port_ping.probe.time.sleep"),
    ):
        summary = run_probes(
            "example.com",
            80,
            count=3,
            should_stop=lambda: True,
        )
    assert summary.total == 0
    assert summary.results == ()


def test_run_probes_count_none_until_stopped() -> None:
    seen: list[int] = []

    def fake_probe(
        host: str,
        port: int,
        *,
        timeout: float,
        sequence: int,
    ) -> ProbeResult:
        seen.append(sequence)
        return ProbeResult(True, host, port, sequence, 1.0, DETAIL_CONNECTED)

    with (
        patch("lupaxa.tcp_port_ping.probe.probe_tcp_port", side_effect=fake_probe),
        patch("lupaxa.tcp_port_ping.probe.time.sleep"),
    ):
        summary = run_probes(
            "example.com",
            80,
            count=None,
            should_stop=lambda: len(seen) >= 2,
        )
    assert seen == [0, 1]
    assert summary.total == 2


def test_run_probes_rejects_zero_count() -> None:
    with pytest.raises(ValueError, match="count"):
        run_probes("example.com", 80, count=0)


def test_summarize_totals() -> None:
    summary = summarize(
        [
            ProbeResult(True, "example.com", 80, 0, 12.3, DETAIL_CONNECTED),
            ProbeResult(False, "example.com", 80, 1, 1000.0, DETAIL_REFUSED),
        ],
    )
    assert summary.total == 2
    assert summary.passed == 1
    assert summary.failed == 1
    assert summary.fail_percent == 50.0
