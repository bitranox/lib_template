from __future__ import annotations

import lib_cli_exit_tools

from . import cli


if __name__ == "__main__":
    try:
        exit_code = int(cli.main())
    except BaseException as exc:  # fallback to shared exit helpers
        lib_cli_exit_tools.print_exception_message(
            trace_back=lib_cli_exit_tools.config.traceback,
            length_limit=10_000 if lib_cli_exit_tools.config.traceback else 500,
        )
        exit_code = lib_cli_exit_tools.get_system_exit_code(exc)
    raise SystemExit(exit_code)
