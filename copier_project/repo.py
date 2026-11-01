from __future__ import annotations

import os
import re
import subprocess
import tempfile
from contextlib import ExitStack, suppress
from dataclasses import InitVar, dataclass, field
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Self

import yaml
from rich import print  # noqa: A004
from rich.panel import Panel
from rich.text import Text

if TYPE_CHECKING:
    from collections.abc import Sequence

SELF_ALIAS = "self"
PROJECT_URL = "https://github.com/smkent/copier-project"


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
        if arg == SELF_ALIAS:
            arg = PROJECT_URL
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
class RepoWorktree(ExitStack):
    path: Path = field(init=False)
    repo: RepoTarget
    branch: str

    def __post_init__(self) -> None:
        super().__init__()

    def __enter__(self) -> Self:
        self.path = (
            Path(self.enter_context(tempfile.TemporaryDirectory()))
            / "worktree"
        )
        self.run(
            ["git", "clone", self.repo.url, str(self.path)], set_cwd=False
        )
        self.run(
            [
                "git",
                "remote",
                "set-url",
                "--push",
                "origin",
                self.repo.push_url,
            ],
        )
        self.run(["mise", "install"] if self.use_mise() else ["poe", "setup"])
        self.run(["git", "checkout", "-b", self.branch])
        return self

    def use_mise(self) -> bool:
        return (self.path / "mise.toml").is_file()

    def run(
        self, cmd: list[str], *, set_cwd: bool = True, **kwargs: Any
    ) -> subprocess.CompletedProcess[str]:
        if set_cwd:
            kwargs.setdefault("cwd", self.path)
        kwargs.setdefault("check", True)
        kwargs.setdefault("text", True)
        cmd_text = Text(" ".join(cmd), style="color(153)")
        txt = Text.assemble(
            Text(f"{self.repo.github_repo} => ", style="bold"),
            cmd_text,
        )
        print(Panel(txt, expand=False, border_style="white dim"))
        return subprocess.run(cmd, **kwargs)  # noqa: S603 PLW1510

    def run_task(
        self, name: str, **kwargs: Any
    ) -> subprocess.CompletedProcess[str]:
        task_runner = (
            ["mise", "run"] if self.use_mise() else ["uv", "run", "poe"]
        )
        return self.run([*task_runner, name], **kwargs)

    def git_status(self) -> dict[str, str]:
        return {
            line[3:]: line[:2]
            for line in self.run(
                ["git", "status", "--porcelain"], capture_output=True
            ).stdout.splitlines()
        }

    @staticmethod
    def has_conflicts(status: dict[str, str]) -> bool:
        conflict_codes = {"UU", "AA", "DD", "AU", "UA", "DU", "UD"}
        return bool(set(status.values()) & conflict_codes)

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
