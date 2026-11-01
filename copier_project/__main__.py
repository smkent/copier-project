from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Annotated

from rich import print  # noqa: A004
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from typer import Argument, Exit, Option, Typer

from . import version as package_version
from .repo import RepoTarget
from .update import UpdateAction

if TYPE_CHECKING:
    from collections.abc import Sequence


console = Console()


class Args:
    Repos = Annotated[
        list[str],
        Argument(
            help=(
                "Repositories to update. Accepts gh:user/repo"
                " or github.com/user/repo."
            )
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


class UpdateStatus(Enum):
    UPDATED = "bold green"
    CURRENT = "bold blue"
    FAILED = "bold red"

    @property
    def formatted_name(self) -> Text:
        return Text(f"{self.name:<7}", style=self.value)


@dataclass
class UpdateResult:
    repo: RepoTarget
    status: UpdateStatus
    exception: Exception | None = None
    pr_url: str | None = None


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
    results = []

    repo_targets = {(target := RepoTarget(repo)).url: target for repo in repos}
    for target in repo_targets.values():
        try:
            pr_url = UpdateAction(
                target,
                branch=branch,
                vcs_ref=vcs_ref,
                dry_run=dry_run,
                allow_empty=allow_empty,
            )()
            if pr_url:
                results.append(
                    UpdateResult(target, UpdateStatus.UPDATED, pr_url=pr_url)
                )
            else:
                results.append(UpdateResult(target, UpdateStatus.CURRENT))
        except Exception as exc:  # noqa: BLE001
            console.print_exception()
            results.append(
                UpdateResult(target, status=UpdateStatus.FAILED, exception=exc)
            )

    _print_summary(results, dry_run=dry_run)
    if any(r.status == UpdateStatus.FAILED for r in results):
        raise Exit(1)


@cli.command(help=f"Show version ({package_version}) and exit.")
def version() -> None:
    console.print(package_version, highlight=False)


def _print_summary(results: Sequence[UpdateResult], *, dry_run: bool) -> None:
    if not results:
        return
    grid = Table.grid(padding=(0, 1), expand=True)
    grid.add_column()
    grid.add_column()
    grid.add_column()
    for result in sorted(results, key=lambda r: r.repo.github_repo):
        grid.add_row(
            result.status.formatted_name,
            Text.from_markup(
                f"[link={result.repo.url}]{result.repo.github_repo}[/link]",
                style="bold",
            ),
            Text(str(result.pr_url or result.exception)),
        )
    title = Text("Update Results", style="bold")
    if dry_run:
        title += Text(" (dry run)", style="green")
    print(
        Panel(grid, title=title, title_align="left", expand=False, padding=1)
    )


def setup_env() -> None:
    os.environ.pop("VIRTUAL_ENV", default=None)
    os.environ["TERMINAL_WIDTH"] = str(
        min(shutil.get_terminal_size().columns, 100)
    )


def main() -> None:
    setup_env()
    cli()


if __name__ == "__main__":
    main()
