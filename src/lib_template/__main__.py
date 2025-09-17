from __future__ import annotations

import lib_cli_exit_tools

from .cli import main


if __name__ == "__main__":
    try:
        exit_code = int(main())
    except BaseException as exc:  # fallback to shared exit helpers
        lib_cli_exit_tools.print_exception_message()
        exit_code = lib_cli_exit_tools.get_system_exit_code(exc)
    raise SystemExit(exit_code)
