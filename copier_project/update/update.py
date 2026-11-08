from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from rich import print  # noqa: A004
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from typer import Exit

from .project import UpdateProject, UpdateResult, UpdateStatus
from .repo import RepoTarget

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass
class UpdateAction:
    repos: Sequence[str]
    vcs_ref: str | None = None
    dry_run: bool = False
    allow_empty: bool = False
    branch: str = "updates"

    @cached_property
    def repo_targets(self) -> dict[str, RepoTarget]:
        return {
            (target := RepoTarget(repo)).url: target for repo in self.repos
        }

    def __call__(self) -> None:
        results = []
        for target in self.repo_targets.values():
            result = UpdateProject(
                target,
                branch=self.branch,
                vcs_ref=self.vcs_ref,
                dry_run=self.dry_run,
                allow_empty=self.allow_empty,
            )()
            results.append((target, result))
        self._print_summary(results, dry_run=self.dry_run)
        if any(r[1].status == UpdateStatus.FAILED for r in results):
            raise Exit(1)

    def _print_summary(
        self,
        results: Sequence[tuple[RepoTarget, UpdateResult]],
        *,
        dry_run: bool,
    ) -> None:
        if not results:
            return
        grid = Table.grid(padding=(0, 1), expand=True)
        grid.add_column()
        grid.add_column()
        grid.add_column()
        for repo, result in sorted(results, key=lambda r: r[0].github_repo):
            grid.add_row(
                result.status.formatted_name,
                Text.from_markup(
                    f"[link={repo.url}]{repo.github_repo}[/link]",
                    style="bold",
                ),
                Text(str(result.pr_url or result.exception)),
            )
        title = Text("Update Results", style="bold")
        if dry_run:
            title += Text(" (dry run)", style="green")
        print(
            Panel(
                grid, title=title, title_align="left", expand=False, padding=1
            )
        )
