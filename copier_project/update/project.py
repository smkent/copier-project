from __future__ import annotations

import json
import subprocess
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

from rich.text import Text

from .constants import COPIER_CMD, PROJECT_URL

if TYPE_CHECKING:
    from collections.abc import Generator

    from .repo import RepoTarget, RepoWorktree


class UpdateStatus(Enum):
    UPDATED = "bold green"
    CURRENT = "bold blue"
    FAILED = "bold red"

    @property
    def formatted_name(self) -> Text:
        return Text(f"{self.name:<7}", style=self.value)


@dataclass
class UpdateResult:
    status: UpdateStatus
    exception: Exception | None = None
    pr_url: str | None = None


@dataclass
class UpdateProject:
    repo: RepoTarget
    branch: str
    vcs_ref: str | None = None
    dry_run: bool = field(default=False, kw_only=True)
    allow_empty: bool = field(default=False, kw_only=True)

    def __call__(self) -> UpdateResult:
        try:
            with self.repo.worktree(branch=self.branch) as worktree:
                return self._run(worktree)
        except Exception as e:  # noqa: BLE001
            return UpdateResult(status=UpdateStatus.FAILED, exception=e)

    @contextmanager
    def _success_or_shell(
        self, repo: RepoWorktree, name: str
    ) -> Generator[None]:
        try:
            yield
        except subprocess.CalledProcessError:
            print(  # noqa: T201
                f"{name} failed. Fix errors and exit the shell to continue."
            )
            repo.shell()

    def _run(self, repo: RepoWorktree) -> UpdateResult:
        """Run copier update in the repo worktree."""
        copier_status = json.loads(
            repo.run(
                [*COPIER_CMD, "check-update", "--output-format", "json"],
                capture_output=True,
            ).stdout.strip()
        )
        start_ref = "v" + copier_status["current_version"]
        end_ref = self.vcs_ref or ("v" + copier_status["latest_version"])
        if not copier_status.get("update_available", False):
            return UpdateResult(status=UpdateStatus.CURRENT)
        repo.run(["git", "checkout", "-b", self.branch])
        repo.run(
            [
                *COPIER_CMD,
                "update",
                "--skip-answered",
                "--vcs-ref",
                end_ref,
            ]
        )

        status = repo.git_status()
        if not status or (
            not self.allow_empty and status.keys() == {".copier-answers.yml"}
        ):
            return UpdateResult(status=UpdateStatus.CURRENT)

        if repo.has_conflicts(status):
            print(  # noqa: T201
                "Conflicts detected."
                " Resolve them and exit the shell to continue."
            )
            repo.shell()
            status = repo.git_status()
            if repo.has_conflicts(status):
                raise RuntimeError("Conflicts remain, aborting")

        if repo.use_mise():
            with self._success_or_shell(repo, "`mise install`"):
                repo.run(["mise", "install"])
        with self._success_or_shell(repo, "Lint/test"):
            repo.run_task("lt")

        title = f"Apply template updates from {start_ref} to {end_ref}"
        body = ""
        if start_ref and end_ref and start_ref != end_ref:
            body = f"{PROJECT_URL}/compare/{start_ref}...{end_ref}"
        repo.run(["git", "add", "-A"])
        repo.run(["git", "commit", "-m", f"{title}\n\n{body}".strip()])

        if self.dry_run:
            return UpdateResult(
                status=UpdateStatus.UPDATED,
                pr_url=f"Update from {start_ref} to {end_ref}",
            )

        repo.run(
            ["git", "push", "-u", "origin", repo.branch, "--force-with-lease"]
        )
        pr_url = repo.open_pr(title, body)
        return UpdateResult(status=UpdateStatus.UPDATED, pr_url=pr_url)
