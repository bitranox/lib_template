from __future__ import annotations

import runpy
from typing import Any

import signal

from click.testing import CliRunner
import click
import pytest

import lib_cli_exit_tools
from lib_template import hello_world
from lib_template import cli as cli_mod


def test_hello_world_prints_greeting(capsys: pytest.CaptureFixture[str]) -> None:
    hello_world()
    captured = capsys.readouterr()
    assert captured.out == "Hello World\n"
    assert captured.err == ""


def test_cli_info_command_sets_traceback(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    monkeypatch.setattr(lib_cli_exit_tools.config, "traceback", False, raising=False)
    monkeypatch.setattr(cli_mod.__init__conf__, "print_info", lambda: calls.append("info"))

    runner = CliRunner()
    result = runner.invoke(cli_mod.cli, ["--traceback", "info"])

    assert result.exit_code == 0
    assert calls == ["info"]
    assert lib_cli_exit_tools.config.traceback is True


def test_main_success_path(monkeypatch: pytest.MonkeyPatch) -> None:
    called: dict[str, Any] = {}

    monkeypatch.setattr(cli_mod, "_install_signal_handlers", lambda: called.setdefault("install", True))

    def fake_cli_main(*, args: Any, standalone_mode: bool, prog_name: str) -> None:  # noqa: D401
        called["cli"] = dict(args=args, standalone_mode=standalone_mode, prog_name=prog_name)

    monkeypatch.setattr(cli_mod.cli, "main", fake_cli_main)
    monkeypatch.setattr(lib_cli_exit_tools, "flush_streams", lambda: called.setdefault("flush", True))

    result = cli_mod.main(["info"])

    assert result == 0
    assert called == {
        "install": True,
        "cli": {"args": ["info"], "standalone_mode": False, "prog_name": cli_mod.__init__conf__.shell_command},
        "flush": True,
    }


def test_main_exception_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli_mod, "_install_signal_handlers", lambda: None)

    def raise_error(*, args: Any, standalone_mode: bool, prog_name: str) -> None:  # noqa: D401
        raise RuntimeError("boom")

    caught: dict[str, Any] = {}

    def fake_print() -> None:
        caught["print"] = True

    def fake_exit_code(exc: BaseException) -> int:
        caught["exc"] = exc
        return 77

    monkeypatch.setattr(cli_mod.cli, "main", raise_error)
    monkeypatch.setattr(lib_cli_exit_tools, "print_exception_message", fake_print)
    monkeypatch.setattr(lib_cli_exit_tools, "get_system_exit_code", fake_exit_code)
    monkeypatch.setattr(lib_cli_exit_tools, "flush_streams", lambda: caught.setdefault("flush", True))

    result = cli_mod.main([])

    assert result == 77
    assert caught["print"] is True
    assert isinstance(caught["exc"], RuntimeError)
    assert caught["flush"] is True


def test_module_main(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("lib_template.cli.main", lambda: 0)

    with pytest.raises(SystemExit) as exc:
        runpy.run_module("lib_template.__main__", run_name="__main__")

    assert exc.value.code == 0


def test_handle_exception_signal_branches(monkeypatch: pytest.MonkeyPatch) -> None:
    messages: list[tuple[str, bool]] = []

    def fake_echo(msg: str, *, err: bool = False) -> None:
        messages.append((msg, err))

    monkeypatch.setattr(cli_mod.click, "echo", fake_echo)

    assert cli_mod._handle_exception(cli_mod.SigIntError()) == 130
    assert cli_mod._handle_exception(cli_mod.SigTermError()) == 143
    assert cli_mod._handle_exception(cli_mod.SigBreakError()) == 149

    assert messages == [
        ("Aborted (SIGINT).", True),
        ("Terminated (SIGTERM/SIGBREAK).", True),
        ("Terminated (SIGBREAK).", True),
    ]


def test_handle_exception_broken_pipe_and_system_exit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(lib_cli_exit_tools.config, "broken_pipe_exit_code", 201, raising=False)
    monkeypatch.setattr(cli_mod.click, "echo", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("no echo")))

    assert cli_mod._handle_exception(BrokenPipeError()) == 201
    assert cli_mod._handle_exception(SystemExit("5")) == 5


def test_handle_exception_generic_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    caught: dict[str, Any] = {}

    def fake_print() -> None:
        caught["printed"] = True

    def fake_code(exc: BaseException) -> int:
        caught["exc"] = exc
        return 44

    monkeypatch.setattr(lib_cli_exit_tools, "print_exception_message", fake_print)
    monkeypatch.setattr(lib_cli_exit_tools, "get_system_exit_code", fake_code)

    assert cli_mod._handle_exception(RuntimeError("boom")) == 44
    assert caught["printed"] is True
    assert isinstance(caught["exc"], RuntimeError)

    lib_cli_exit_tools.config.traceback = True
    with pytest.raises(RuntimeError):
        cli_mod._handle_exception(RuntimeError("boom"))
    lib_cli_exit_tools.config.traceback = False


def test_module_main_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_error() -> int:
        raise RuntimeError("boom")

    signals: list[str] = []

    def fake_print() -> None:
        signals.append("printed")

    def fake_code(exc: BaseException) -> int:
        signals.append(f"code:{exc}")
        return 88

    monkeypatch.setattr("lib_template.cli.main", raise_error)
    monkeypatch.setattr(lib_cli_exit_tools, "print_exception_message", fake_print)
    monkeypatch.setattr(lib_cli_exit_tools, "get_system_exit_code", fake_code)

    with pytest.raises(SystemExit) as exc:
        runpy.run_module("lib_template.__main__", run_name="__main__")

    assert exc.value.code == 88
    assert signals == ["printed", "code:boom"]


def test_signal_handlers_raise(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(cli_mod.SigIntError):
        cli_mod._sigint_handler(signal.SIGINT, None)
    with pytest.raises(cli_mod.SigTermError):
        cli_mod._sigterm_handler(signal.SIGTERM, None)

    recorded: list[tuple[Any, Any]] = []

    def fake_signal(sig: int, handler: Any) -> None:
        recorded.append((sig, handler))

    monkeypatch.setattr(cli_mod, "is_posix", True, raising=False)
    monkeypatch.setattr(cli_mod, "is_windows", False, raising=False)
    monkeypatch.setattr(cli_mod.signal, "signal", fake_signal)
    cli_mod._install_signal_handlers()

    assert recorded[0] == (signal.SIGINT, cli_mod._sigint_handler)
    assert recorded[1] == (signal.SIGTERM, cli_mod._sigterm_handler)

    monkeypatch.setattr(cli_mod, "is_posix", False, raising=False)
    monkeypatch.setattr(cli_mod, "is_windows", True, raising=False)
    recorded.clear()
    fake_break = object()
    monkeypatch.setattr(cli_mod.signal, "SIGBREAK", fake_break, raising=False)
    cli_mod._install_signal_handlers()
    assert recorded[0][0] == signal.SIGINT
    sigbreak_handler = recorded[1][1]
    with pytest.raises(cli_mod.SigBreakError):
        sigbreak_handler(fake_break, None)


def test_handle_exception_click_and_system_exit(monkeypatch: pytest.MonkeyPatch) -> None:
    class Dummy(click.ClickException):
        def __init__(self) -> None:
            super().__init__("boom")
            self.exit_code = 12
            self.displayed = False

        def show(self) -> None:
            self.displayed = True

    dummy = Dummy()
    assert cli_mod._handle_exception(dummy) == 12
    assert dummy.displayed is True

    assert cli_mod._handle_exception(SystemExit("7")) == 7
    assert cli_mod._handle_exception(SystemExit(object())) == 1


def test_hello_world_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    from lib_template import lib_template as mod

    with pytest.raises(RuntimeError):
        mod.i_should_fail()
