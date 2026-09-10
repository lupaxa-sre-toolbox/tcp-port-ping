"""CLI entrypoint."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from lupaxa.tcp_port_ping.cli import build_parser, format_probe_line, format_summary, main
from lupaxa.tcp_port_ping.probe import (
    DETAIL_CONNECTED,
    DETAIL_REFUSED,
    DETAIL_TIMEOUT,
    ProbeResult,
    ProbeSummary,
    summarize,
)
from lupaxa.tcp_port_ping.version import get_version

_BASE = ["--server", "example.com", "--port", "80"]


def test_help_exits_zero() -> None:
    assert main(["--help"]) == 0


def test_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--version"]) == 0
    assert get_version() in capsys.readouterr().out


def test_parser_requires_port() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args(["--server", "example.com"])


def test_parser_defaults() -> None:
    args = build_parser().parse_args(_BASE)
    assert args.server == "example.com"
    assert args.port == 80
    assert args.delay == 1.0
    assert args.count is None
    assert args.timeout == 1.0


def test_parser_overrides() -> None:
    args = build_parser().parse_args(
        [
            *_BASE,
            "--port",
            "443",
            "--delay",
            "0.25",
            "--count",
            "3",
            "--timeout",
            "2.5",
        ],
    )
    assert args.port == 443
    assert args.delay == 0.25
    assert args.count == 3
    assert args.timeout == 2.5


def test_parser_rejects_non_positive_timeout() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args([*_BASE, "--timeout", "0"])


def test_parser_rejects_negative_delay() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args([*_BASE, "--delay", "-1"])


def test_parser_rejects_out_of_range_port() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args([*_BASE, "--port", "70000"])


def test_parser_rejects_zero_count() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args([*_BASE, "--count", "0"])


def test_format_success_and_summary() -> None:
    result = ProbeResult(True, "example.com", 80, 0, 12.3, DETAIL_CONNECTED)
    line = format_probe_line(result)
    assert "Connected to example.com[80]" in line
    assert "tcp_seq=0" in line
    assert "12.30 ms" in line
    failed = ProbeResult(False, "example.com", 80, 1, 1000.0, DETAIL_REFUSED)
    text = format_summary(summarize([result, failed]))
    assert "[2/1/1]" in text
    assert "50.00%" in text


def test_format_failure_uses_original_wording() -> None:
    timeout = ProbeResult(False, "example.com", 80, 1, 1000.0, DETAIL_TIMEOUT)
    refused = ProbeResult(False, "example.com", 80, 2, 1.0, DETAIL_REFUSED)
    os_err = ProbeResult(False, "example.com", 80, 3, 1.0, "OS error: network is unreachable")
    assert format_probe_line(timeout) == "Connection timed out!"
    assert format_probe_line(refused) == "Port is closed!!!"
    assert format_probe_line(os_err) == "OS Error: network is unreachable"


def test_main_success(capsys: pytest.CaptureFixture[str]) -> None:
    summary = ProbeSummary(
        total=1,
        passed=1,
        failed=0,
        fail_percent=0.0,
        results=(ProbeResult(True, "example.com", 80, 0, 4.5, DETAIL_CONNECTED),),
    )
    with patch("lupaxa.tcp_port_ping.cli.run_probes", return_value=summary) as run:
        assert main([*_BASE, "--count", "1"]) == 0
    run.assert_called_once()
    kwargs = run.call_args.kwargs
    assert kwargs["count"] == 1
    assert kwargs["timeout"] == 1.0
    assert "should_stop" not in kwargs
    captured = capsys.readouterr().out
    assert "Total/Pass/Fail" in captured
    assert "[1/1/0]" in captured


def test_main_failure_exits_one(capsys: pytest.CaptureFixture[str]) -> None:
    summary = ProbeSummary(
        total=1,
        passed=0,
        failed=1,
        fail_percent=100.0,
        results=(ProbeResult(False, "example.com", 80, 0, 1000.0, DETAIL_REFUSED),),
    )
    with patch("lupaxa.tcp_port_ping.cli.run_probes", return_value=summary):
        assert main([*_BASE, "--count", "1"]) == 1
    assert "Failed: 100.00%" in capsys.readouterr().out


def test_main_interrupt_exits_zero_immediately(capsys: pytest.CaptureFixture[str]) -> None:
    result = ProbeResult(False, "example.com", 80, 0, 1000.0, DETAIL_TIMEOUT)
    handlers: list = []

    def capture(_signum: int, handler: object) -> object:
        handlers.append(handler)
        return lambda *_args: None

    def fake_run(*_args: object, **kwargs: object) -> None:
        on_result = kwargs["on_result"]
        assert callable(on_result)
        on_result(result)
        handlers[-1](2, None)

    with (
        patch("lupaxa.tcp_port_ping.cli.run_probes", side_effect=fake_run),
        patch("lupaxa.tcp_port_ping.cli.signal.signal", side_effect=capture),
    ):
        assert main([*_BASE, "--count", "1"]) == 0
    captured = capsys.readouterr().out
    assert "Connection timed out!" in captured
    assert "Total/Pass/Fail" in captured
    assert "[1/0/1]" in captured
