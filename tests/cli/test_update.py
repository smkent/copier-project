"""Tests for the copier-project update management command."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock, _Call, call, patch

import pytest
import yaml

from copier_project.__main__ import main, update
from copier_project.repo import PROJECT_URL, SELF_ALIAS
from tests.template.utils import template

if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Sequence

    from tests.utils import DisallowCallable


DEFAULT_BRANCH_NAME = "fhqwhgads"
DEFAULT_END_REF = "v0.22.2"


@pytest.fixture(params=["v0.16.2"])
def start_ref(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture(params=[DEFAULT_END_REF])
def end_ref(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture
def mock_shell() -> Path:
    shell = "/bin/false"
    os.environ["SHELL"] = shell
    return Path(shell)


@pytest.fixture
def origin(tmp_path: Path, disallow_subprocess: DisallowCallable) -> Path:
    origin_path = tmp_path / "origin.git"
    with disallow_subprocess.pause():
        subprocess.run(  # noqa: S603
            [
                "git",
                "init",
                "--bare",
                str(origin_path),
                "-b",
                DEFAULT_BRANCH_NAME,
            ],
            check=True,
            capture_output=True,
        )
    return origin_path


@pytest.fixture
def create_project(
    disallow_subprocess: DisallowCallable,
    render_template_common: Callable[..., Path],
    origin: Path,
) -> Callable[..., Path]:

    def _vcs_ref_timestamp(ref: str) -> str:
        with disallow_subprocess.pause():
            return subprocess.run(  # noqa: S603
                ["git", "log", "-n", "1", "--format=%aI", str(ref), "--"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()

    def _create(
        vcs_ref: str,
        postcreate: Callable[[Path], None] | None = None,
        **kwargs: Any,
    ) -> Path:
        project = render_template_common(vcs_ref=vcs_ref, **kwargs)
        timestamp = _vcs_ref_timestamp(vcs_ref)
        for cmd in (
            ["git", "init", "-b", DEFAULT_BRANCH_NAME],
            ["git", "remote", "add", "origin", str(origin)],
            ["uv", "sync", f"--exclude-newer={timestamp}"],
            ["uv", "sync"],
            ["git", "add", "."],
            ["git", "commit", "-m", "init from template"],
            ["git", "push", "-u", "origin", DEFAULT_BRANCH_NAME],
        ):
            with disallow_subprocess.pause():
                subprocess.run(  # noqa: S603
                    cmd, cwd=project, check=True, capture_output=True
                )
        if postcreate:
            postcreate(project)
        return project

    return _create


@pytest.fixture
def mock_temp_dir(tmp_path: Path) -> Generator[Path]:
    with patch.object(
        tempfile.TemporaryDirectory, "__enter__", return_value=tmp_path
    ):
        yield tmp_path


@pytest.fixture
def worktree(mock_temp_dir: Path) -> Path:
    return mock_temp_dir / "worktree"


@pytest.fixture(
    params=(
        pytest.param(True, id="dry_run"),
        pytest.param(False, id="live"),
    )
)
def dry_run(request: pytest.FixtureRequest) -> bool:
    return request.param


@dataclass
class ExpectRun:
    disallow_subprocess: DisallowCallable
    mock_shell: Path
    origin: Path
    worktree: Path
    expected_calls: list[_Call] = field(default_factory=list, init=False)

    @contextmanager
    def patch(
        self,
        *,
        mock: bool = True,
        has_any: bool = False,
        shell_callback: Callable[[], None] | None = None,
    ) -> Generator[MagicMock]:

        subp_run = subprocess.run

        def _run(cmd: Sequence[str], *args: Any, **kwargs: Any) -> Any:
            if cmd[0] == str(self.mock_shell):
                if shell_callback:
                    return shell_callback()
                return MagicMock()
            if tuple(cmd[:2]) == ("copier", "check-update"):
                if mock:
                    current_version = "11.38.0"
                    latest_version = current_version
                else:
                    current_version = yaml.safe_load(
                        (self.worktree / ".copier-answers.yml").read_text()
                    )["_commit"].removeprefix("v")
                    latest_version = DEFAULT_END_REF.removeprefix("v")
                data = {
                    "update_available": (current_version != latest_version),
                    "current_version": current_version,
                    "latest_version": latest_version,
                }
                return SimpleNamespace(stdout=json.dumps(data))
            if mock:
                return MagicMock()
            if tuple(cmd[:3]) == ("copier", "update", "--skip-answered"):
                cmd = [*cmd[:2], "--defaults", "--vcs-ref", DEFAULT_END_REF]
            cmd = [
                (
                    str(self.origin)
                    if arg.startswith(
                        ("https://github.com/", "git@github.com:")
                    )
                    else arg
                )
                for arg in cmd
            ]
            if cmd[0] == "gh":
                cmd = ["echo", *cmd]
            with self.disallow_subprocess.pause():
                return subp_run(cmd, *args, **kwargs)

        with patch.object(subprocess, "run", side_effect=_run) as mock_run:
            yield mock_run
        if has_any:
            mock_run.assert_has_calls(self.expected_calls)
        else:
            assert mock_run.call_args_list == self.expected_calls

    def expect(self, cmd: Sequence[str], **kwargs: Any) -> None:
        kwargs.setdefault("check", True)
        kwargs.setdefault("text", True)
        self.expected_calls.append(call(list(cmd), **kwargs))


@pytest.fixture
def expect_run(
    disallow_subprocess: DisallowCallable,
    mock_shell: Path,
    origin: Path,
    worktree: Path,
) -> ExpectRun:
    return ExpectRun(
        disallow_subprocess=disallow_subprocess,
        mock_shell=mock_shell,
        origin=origin,
        worktree=worktree,
    )


def test_main_help(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["copier-project", "--help"])
    with pytest.raises(SystemExit, match=str(0)):
        main()


@pytest.mark.parametrize(
    "project_visibility", template.choices.project_visibility
)
def test_main_update_with_project_current(
    worktree: Path,
    expect_run: ExpectRun,
    create_project: Callable[..., Path],
    project_visibility: str,
    end_ref: str,
    *,
    dry_run: bool,
) -> None:
    create_project(vcs_ref=end_ref, project_visibility=project_visibility)
    expect_run.expect(
        ["git", "clone", "https://github.com/ness/pkfire", str(worktree)]
    )
    for cmd in [
        [
            *["git", "remote", "set-url", "--push", "origin"],
            "git@github.com:ness/pkfire.git",
        ],
        [*["mise", "install"]],
        [*["git", "checkout", "-b", "updates"]],
    ]:
        expect_run.expect(cmd, cwd=worktree)
    expect_run.expect(
        ["copier", "check-update", "--output-format", "json"],
        cwd=worktree,
        capture_output=True,
    )
    with expect_run.patch(mock=False):
        update(["gh:ness/pkfire"], vcs_ref=end_ref, dry_run=dry_run)


def test_main_update_error(
    disallow_subprocess: DisallowCallable,
    worktree: Path,
    mock_shell: Path,
    expect_run: ExpectRun,
    create_project: Callable[..., Path],
    start_ref: str,
    end_ref: str,
) -> None:
    def _postcreate(project: Path) -> None:
        (project / "AGENTS.md").write_text("Overwritten file, no newline")
        for cmd in (
            ["git", "add", "."],
            ["git", "commit", "-m", "Add conflicting change"],
            ["git", "push"],
        ):
            with disallow_subprocess.pause():
                subprocess.run(  # noqa: S603
                    cmd, cwd=project, check=True, capture_output=True
                )

    create_project(vcs_ref=start_ref, postcreate=_postcreate)
    commit_message = os.linesep.join(
        (
            f"Apply template updates from {start_ref} to {end_ref}",
            "",
            (
                f"https://github.com/smkent/copier-project/compare/"
                f"{start_ref}...{end_ref}"
            ),
        )
    )

    def _shell() -> None:
        with disallow_subprocess.pause():
            for cmd in (
                ["git", "checkout", "--ours", "AGENTS.md"],
                ["git", "reset", "AGENTS.md"],
            ):
                subprocess.check_call(cmd, cwd=worktree)  # noqa: S603

    expect_run.expect(
        ["git", "clone", "https://github.com/ness/pkfire", str(worktree)]
    )
    for cmd in [
        [
            *["git", "remote", "set-url", "--push", "origin"],
            "git@github.com:ness/pkfire.git",
        ],
        [*["mise", "install"]],
        [*["git", "checkout", "-b", "updates"]],
    ]:
        expect_run.expect(cmd, cwd=worktree)
    expect_run.expect(
        ["copier", "check-update", "--output-format", "json"],
        cwd=worktree,
        capture_output=True,
    )
    expect_run.expect(
        ["copier", "update", "--skip-answered", "--vcs-ref", end_ref],
        cwd=worktree,
    )
    expect_run.expect(
        ["git", "status", "--porcelain"], cwd=worktree, capture_output=True
    )
    expect_run.expect([str(mock_shell)], cwd=worktree)
    expect_run.expect(
        ["git", "status", "--porcelain"], cwd=worktree, capture_output=True
    )
    expect_run.expect(["mise", "install"], cwd=worktree)
    expect_run.expect(["mise", "run", "lt"], cwd=worktree)
    expect_run.expect([str(mock_shell)], cwd=worktree)
    for cmd in [
        [*["git", "add", "-A"]],
        [*["git", "commit", "-m", commit_message]],
    ]:
        expect_run.expect(cmd, cwd=worktree)

    with expect_run.patch(mock=False, shell_callback=_shell):
        update(["gh:ness/pkfire"], dry_run=True)


@pytest.mark.parametrize(
    ("arg", "repo"),
    [
        pytest.param(arg, repo, id=arg)
        for repo in ["ness/pkfire", "Ness/PK_Thunder-Alpha"]
        for base in [
            *[repo, f"gh:{repo}", f"github.com/{repo}"],
            *[
                f"{proto}{user}@github.com:{repo}"
                for user in ("git", repo.split("/", 1)[0])
                for proto in ("", "ssh://", "git+ssh://")
            ],
            *[f"{proto}://github.com/{repo}" for proto in ("http", "https")],
        ]
        for base_dotgit in [base, f"{base}.git"]
        for arg in [base_dotgit, f"{base_dotgit}/"]
    ],
)
def test_main_update_repo_arguments(
    worktree: Path, expect_run: ExpectRun, arg: str, repo: str
) -> None:
    expect_run.expect(
        ["git", "clone", f"https://github.com/{repo}", str(worktree)]
    )
    with expect_run.patch(mock=True, has_any=True):
        update([arg], dry_run=True)


def test_main_update_repo_arguments_self(
    worktree: Path, expect_run: ExpectRun
) -> None:
    expect_run.expect(["git", "clone", PROJECT_URL, str(worktree)])
    with expect_run.patch(mock=True, has_any=True):
        update([SELF_ALIAS], dry_run=True)


@pytest.mark.parametrize(
    "project_visibility", template.choices.project_visibility
)
def test_main_update_with_project(
    worktree: Path,
    expect_run: ExpectRun,
    create_project: Callable[..., Path],
    project_visibility: str,
    end_ref: str,
    start_ref: str,
    *,
    dry_run: bool,
) -> None:
    create_project(vcs_ref=start_ref, project_visibility=project_visibility)
    commit_message = os.linesep.join(
        (
            f"Apply template updates from {start_ref} to {end_ref}",
            "",
            (
                f"https://github.com/smkent/copier-project/compare/"
                f"{start_ref}...{end_ref}"
            ),
        )
    )

    expect_run.expect(
        ["git", "clone", "https://github.com/ness/pkfire", str(worktree)]
    )
    for cmd in [
        [
            *["git", "remote", "set-url", "--push", "origin"],
            "git@github.com:ness/pkfire.git",
        ],
        [*["mise", "install"]],
        [*["git", "checkout", "-b", "updates"]],
    ]:
        expect_run.expect(cmd, cwd=worktree)
    expect_run.expect(
        ["copier", "check-update", "--output-format", "json"],
        cwd=worktree,
        capture_output=True,
    )
    expect_run.expect(
        ["copier", "update", "--skip-answered", "--vcs-ref", end_ref],
        cwd=worktree,
    )
    expect_run.expect(
        ["git", "status", "--porcelain"], cwd=worktree, capture_output=True
    )
    expect_run.expect(["mise", "install"], cwd=worktree)
    for cmd in [
        [*["mise", "run", "lt"]],
        [*["git", "add", "-A"]],
        [*["git", "commit", "-m", commit_message]],
    ]:
        expect_run.expect(cmd, cwd=worktree)
    if not dry_run:
        for cmd in [
            ["git", "push", "-u", "origin", "updates", "--force-with-lease"],
        ]:
            expect_run.expect(cmd, cwd=worktree)

        title, _, *body = commit_message.splitlines()
        expect_run.expect(
            [
                "gh",
                "pr",
                "create",
                "--title",
                title,
                "--body",
                os.linesep.join(body),
                "--head",
                "updates",
            ],
            cwd=worktree,
            check=False,
            capture_output=True,
        )
    with expect_run.patch(mock=False):
        update(["gh:ness/pkfire"], dry_run=dry_run)
