from __future__ import annotations

import os
import shutil
from typing import Annotated

from typer import Argument, Exit, Option, Typer

from . import version as package_version
from .console import console
from .update.repo import RepoTarget
from .update.update import UpdateAction


class Args:
    Repos = Annotated[
        list[RepoTarget],
        Argument(
            parser=RepoTarget,
            help=(
                "Repositories to update. Accepts gh:user/repo"
                " or github.com/user/repo."
            ),
        ),
    ]
    DryRun = Annotated[
        bool, Option("--dry-run", "-n", help="Skip push and PR creation.")
    ]


cli = Typer(
    help="copier-project utilities",
    add_completion=False,
    no_args_is_help=True,
    pretty_exceptions_enable=False,
    invoke_without_command=True,
)


@cli.callback()
def setup(
    *,
    version_option: Annotated[
        bool, Option("-V", "--version", hidden=True)
    ] = False,
) -> None:
    if version_option:
        version()
        raise Exit


@cli.command()
def update(
    repos: Args.Repos,
    *,
    vcs_ref: Annotated[
        str | None, Option("--vcs-ref", "-r", help="Template ref to update to")
    ] = None,
    dry_run: Args.DryRun = False,
    allow_empty: Annotated[
        bool,
        Option(
            "--allow-empty",
            "-e",
            help="Apply update even if template diff is blank.",
        ),
    ] = False,
    branch: Annotated[str, Option(help="Branch name to create.")] = "updates",
) -> None:
    """Apply copier-project template updates to downstream repositories."""
    UpdateAction(
        repos=repos,
        vcs_ref=vcs_ref,
        dry_run=dry_run,
        allow_empty=allow_empty,
        branch=branch,
    )()


@cli.command(help=f"Show version ({package_version}) and exit.")
def version() -> None:
    console.print(package_version, highlight=False)


def setup_env() -> None:
    os.environ.pop("VIRTUAL_ENV", default=None)
    os.environ["TERMINAL_WIDTH"] = str(
        min(shutil.get_terminal_size().columns, 100)
    )


def main() -> None:
    setup_env()
    cli()


if __name__ == "__main__":  # pragma: no cover
    main()
