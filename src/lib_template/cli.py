from __future__ import annotations

from typing import Optional, Sequence

import click

import lib_cli_exit_tools

from . import __init__conf__
from .lib_template import hello_world as _hello_world
from .lib_template import i_should_fail as _fail

CLICK_CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])  # noqa: C408


@click.group(help=__init__conf__.title, context_settings=CLICK_CONTEXT_SETTINGS)
@click.version_option(
    version=__init__conf__.version,
    prog_name=__init__conf__.shell_command,
    message=f"{__init__conf__.shell_command} version {__init__conf__.version}",
)
@click.option(
    "--traceback/--no-traceback",
    is_flag=True,
    default=False,
    help="Show full Python traceback on errors",
)
@click.pass_context
def cli(ctx: click.Context, traceback: bool) -> None:
    """Root CLI group. Stores global opts in context & shared config."""
    ctx.ensure_object(dict)
    ctx.obj["traceback"] = traceback
    lib_cli_exit_tools.config.traceback = traceback


@cli.command("info", context_settings=CLICK_CONTEXT_SETTINGS)
def cli_info() -> None:
    """Print project information."""
    __init__conf__.print_info()


@cli.command("hello", context_settings=CLICK_CONTEXT_SETTINGS)
def cli_hello() -> None:
    """Print the standard hello message."""
    _hello_world()


@cli.command("fail", context_settings=CLICK_CONTEXT_SETTINGS)
def cli_fail() -> None:
    """Trigger the intentional failure helper."""
    _fail()


def cli_main(argv: Optional[Sequence[str]] = None) -> int:
    """Entrypoint returning an exit code via shared run_cli helper."""
    return


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Entrypoint returning an exit code via shared run_cli helper."""
    try:
        exit_code = int(
            lib_cli_exit_tools.run_cli(
                cli,
                argv=list(argv) if argv is not None else None,
                prog_name=__init__conf__.shell_command,
            )
        )
    except BaseException as exc:  # fallback to shared exit helpers
        lib_cli_exit_tools.print_exception_message()
        exit_code = lib_cli_exit_tools.get_system_exit_code(exc)
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
