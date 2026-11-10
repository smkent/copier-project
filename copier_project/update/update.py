from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from rich import print  # noqa: A004
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from typer import Exit

from .project import UpdateProject, UpdateResult, UpdateResultType

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .repo import RepoTarget


@dataclass
class UpdateAction:
    repos: Sequence[RepoTarget]
    vcs_ref: str | None = None
    dry_run: bool = False
    allow_empty: bool = False
    branch: str = "updates"

    def __call__(self) -> None:
        results = []
        for repo in self.repos:
            result = UpdateProject(
                repo,
                branch=self.branch,
                vcs_ref=self.vcs_ref,
                dry_run=self.dry_run,
                allow_empty=self.allow_empty,
            )()
            results.append((repo, result))
        self._print_summary(results)
        if any(r[1].type == UpdateResultType.FAILED for r in results):
            raise Exit(1)

    def _print_summary(
        self, results: Sequence[tuple[RepoTarget, UpdateResult]]
    ) -> None:
        if not results:
            return
        grid = Table.grid(padding=(0, 2), expand=True)
        for _ in range(5):
            grid.add_column()
        grid.add_row(
            *(
                Text(t, style="white bold")
                for t in ("Repository", "Result", "Prev Ref", "New Ref")
            )
        )
        grid.add_row()
        for repo, result in sorted(results, key=lambda r: r[0].github_repo):
            grid.add_row(
                repo.text,
                result.type.formatted_name,
                result.start_ref,
                result.end_ref or "-",
                Text(str(result.pr_url or result.message or " ")),
            )
        title = Text("Update Results", style="bold")
        if self.dry_run:
            title += Text(" (dry run)", style="green")
        print(
            Panel(
                grid, title=title, title_align="left", expand=False, padding=1
            )
        )
