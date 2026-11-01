from __future__ import annotations

import json
import subprocess
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .repo import PROJECT_URL, RepoWorktree

if TYPE_CHECKING:
    from collections.abc import Generator

    from .repo import RepoTarget


@dataclass
class UpdateAction:
    repo: RepoTarget
    branch: str
    vcs_ref: str | None = None
    dry_run: bool = field(default=False, kw_only=True)
    allow_empty: bool = field(default=False, kw_only=True)

    def __call__(self) -> str | None:
        with RepoWorktree.clone(self.repo, branch=self.branch) as worktree:
            return self._run(worktree)

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

    def _run(self, repo: RepoWorktree) -> str | None:
        """Run copier update in the repo worktree."""
        copier_status = json.loads(
            repo.run(
                ["copier", "check-update", "--output-format", "json"],
                capture_output=True,
            ).stdout.strip()
        )
        start_ref = "v" + copier_status["current_version"]
        end_ref = self.vcs_ref or ("v" + copier_status["latest_version"])
        if not copier_status.get("update_available", False):
            return None
        repo.run(["copier", "update", "--skip-answered", "--vcs-ref", end_ref])

        status = repo.git_status()
        if not status or (
            not self.allow_empty and status.keys() == {".copier-answers.yml"}
        ):
            return None

        if repo.has_conflicts(status):
            print(  # noqa: T201
                "Conflicts detected."
                " Resolve them and exit the shell to continue."
            )
            repo.shell()
            status = repo.git_status()
            if repo.has_conflicts(status):
                raise RuntimeError("Conflicts remain, aborting")

        if (repo.path / "mise.toml").is_file():
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
            return f"Update from {start_ref} to {end_ref}"

        repo.run(
            ["git", "push", "-u", "origin", repo.branch, "--force-with-lease"]
        )
        return repo.open_pr(title, body)
