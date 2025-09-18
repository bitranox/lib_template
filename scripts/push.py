from __future__ import annotations

import os
import click
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts._utils import git_branch, run, sync_packaging  # noqa: E402


@click.command(help="Run tests, sync packaging, commit changes if any, and push current branch")
@click.option("--remote", default="origin", show_default=True)
def main(remote: str) -> None:
    click.echo("[push] Running local checks (scripts/test.py)")
    run(["python", "scripts/test.py"])  # type: ignore[list-item]

    click.echo("[push] Sync packaging with pyproject before commit")
    sync_packaging()

    click.echo("[push] Committing and pushing (single attempt)")
    run(["git", "add", "-A"])  # stage all
    staged = run(["bash", "-lc", "! git diff --cached --quiet"], check=False)
    env_message = os.environ.get("COMMIT_MESSAGE")
    default_message = env_message.strip() if env_message else "chore: update"
    if env_message is not None:
        message = default_message
        click.echo(f"[push] Using commit message from COMMIT_MESSAGE: {message}")
    elif sys.stdin.isatty():
        message = click.prompt("[push] Commit message", default=default_message)
    else:
        click.echo("[push] Non-interactive input; using default commit message")
        message = default_message
    message = message.strip() or default_message
    if staged.code != 0:
        click.echo("[push] No staged changes detected; creating empty commit")
    run(["git", "commit", "--allow-empty", "-m", message])  # type: ignore[list-item]
    branch = git_branch()
    run(["git", "push", "-u", remote, branch])  # type: ignore[list-item]


if __name__ == "__main__":
    main()
