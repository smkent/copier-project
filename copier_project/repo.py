from __future__ import annotations

import os
import re
import subprocess
import tempfile
from contextlib import contextmanager, suppress
from dataclasses import InitVar, dataclass, field
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Self

import yaml
from rich import print  # noqa: A004
from rich.panel import Panel
from rich.text import Text

if TYPE_CHECKING:
    from collections.abc import Generator, Sequence


@dataclass(unsafe_hash=True)
class RepoTarget:
    arg: InitVar[str | Path]
    github_repo: str = field(init=False)

    _GITHUB_REGEXES: ClassVar[Sequence[str]] = [
        r"(\.git)?/?$",
        r"^gh\:",
        r"^(https?://)?github.com/",
        r"^((git\+)?ssh://)?([a-zA-Z0-9]+)@github.com:",
    ]

    def __post_init__(self, arg: str | Path) -> None:
        arg = str(arg).strip()
        if ((path := Path(arg)).is_dir()) and (root := self.repo_root(path)):
            arg = root
        for regex in self._GITHUB_REGEXES:
            arg = re.sub(regex, "", arg)
        if not re.fullmatch(r"[\w-]+\/[\w-]+", arg):
            raise ValueError(arg)
        self.github_repo = arg

    def repo_root(self, path: Path) -> str | None:
        with suppress(subprocess.CalledProcessError):
            return subprocess.check_output(
                ["git", "config", "--local", "remote.origin.url"],
                text=True,
                cwd=path,
            ).strip()
        return None

    @cached_property
    def name(self) -> str:
        return self.github_repo.split("/")[-1]

    @property
    def url(self) -> str:
        return f"https://github.com/{self.github_repo}"

    @cached_property
    def push_url(self) -> str:
        return f"git@github.com:{self.github_repo}.git"


@dataclass
class RepoWorktree:
    path: Path
    repo: RepoTarget
    branch: str

    @classmethod
    @contextmanager
    def clone(
        cls, repo: RepoTarget, branch: str
    ) -> Generator[Self, None, None]:
        with tempfile.TemporaryDirectory() as td:
            repo_dir = Path(td) / "worktree"
            cls.run_in(["git", "clone", repo.url, str(repo_dir)], repo=repo)
            cls.run_in(
                [
                    *["git", "remote", "set-url", "--push", "origin"],
                    repo.push_url,
                ],
                repo=repo,
                cwd=repo_dir,
            )
            cls.run_in(
                (
                    ["mise", "install"]
                    if (repo_dir / "mise.toml").is_file()
                    else ["poe", "setup"]
                ),
                repo=repo,
                cwd=repo_dir,
            )
            cls.run_in(
                ["git", "checkout", "-b", branch], repo=repo, cwd=repo_dir
            )
            yield cls(path=repo_dir, repo=repo, branch=branch)

    @classmethod
    def run_in(
        cls, cmd: list[str], *, repo: RepoTarget, **kwargs: Any
    ) -> subprocess.CompletedProcess[str]:
        kwargs.setdefault("check", True)
        kwargs.setdefault("text", True)
        cmd_text = Text(" ".join(cmd), style="color(153)")
        txt = Text.assemble(
            Text(f"{repo.github_repo} => ", style="bold"),
            cmd_text,
        )
        print(Panel(txt, expand=False, border_style="white dim"))
        return subprocess.run(cmd, **kwargs)  # noqa: S603 PLW1510

    def run(
        self, cmd: list[str], **kwargs: Any
    ) -> subprocess.CompletedProcess[str]:
        kwargs.setdefault("cwd", self.path)
        return self.run_in(cmd, repo=self.repo, **kwargs)

    def run_task(
        self, name: str, **kwargs: Any
    ) -> subprocess.CompletedProcess[str]:
        task_runner = (
            ["mise", "run"]
            if (self.path / "mise.toml").is_file()
            else ["uv", "run", "poe"]
        )
        return self.run([*task_runner, name], **kwargs)

    def git_status(self) -> list[str]:
        return self.run(
            ["git", "status", "--porcelain"], capture_output=True
        ).stdout.splitlines()

    @staticmethod
    def has_conflicts(status: list[str]) -> bool:
        conflict_codes = {"UU", "AA", "DD", "AU", "UA", "DU", "UD"}
        return any(line[:2] in conflict_codes for line in status)

    @property
    def template_ref(self) -> str:
        return yaml.safe_load(  # type: ignore[no-any-return]
            (self.path / ".copier-answers.yml").read_text()
        ).get("_commit")

    def shell(self) -> None:
        self.run([os.environ.get("SHELL", "/bin/bash")])

    def open_pr(self, title: str, body: str) -> str:
        result = self.run(
            [
                "gh",
                "pr",
                "create",
                "--title",
                title,
                "--body",
                body,
                "--head",
                self.branch,
            ],
            capture_output=True,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        view = self.run(
            ["gh", "pr", "view", "--json", "url", "--jq", ".url"],
            capture_output=True,
            check=False,
        )
        if view.returncode == 0:
            return view.stdout.strip()
        raise RuntimeError(f"gh pr create failed: {result.stderr.strip()}")
