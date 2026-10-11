from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .repo import RepoWorktree

if TYPE_CHECKING:
    from .repo import RepoTarget

TEMPLATE_REPO_URL = "https://github.com/smkent/copier-python"


@dataclass
class UpdateAction:
    repo: RepoTarget
    branch: str
    vcs_ref: str | None = None
    dry_run: bool = field(default=False, kw_only=True)

    def __call__(self) -> str | None:
        with RepoWorktree.clone(self.repo, branch=self.branch) as worktree:
            return self._run(worktree)

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
        if not status:
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

        try:
            repo.run(["mise", "install"])
        except subprocess.CalledProcessError:
            print(  # noqa: T201
                "Lint/test failed. Fix errors and exit the shell to continue."
            )
            repo.shell()

        try:
            repo.run_task("lt")
        except subprocess.CalledProcessError:
            print(  # noqa: T201
                "Lint/test failed. Fix errors and exit the shell to continue."
            )
            repo.shell()

        title = "Apply template updates"
        body = ""
        if start_ref and end_ref and start_ref != end_ref:
            ref_range = f"{start_ref}...{end_ref}"
            body = os.linesep.join(
                (
                    f"Applied updates from template: {ref_range}",
                    f"{TEMPLATE_REPO_URL}/compare/{ref_range}",
                )
            )
        repo.run(["git", "add", "-A"])
        repo.run(["git", "commit", "-m", f"{title}\n\n{body}".strip()])

        if self.dry_run:
            return None

        repo.run(
            ["git", "push", "-u", "origin", repo.branch, "--force-with-lease"]
        )
        return repo.open_pr(title, body)
