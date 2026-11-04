from __future__ import annotations

import subprocess
import tomllib
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import cached_property
from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from pathlib import Path

    from tests.utils import DisallowCallable


class VersionApproach(Enum):
    IMPORTLIB_METADATA = auto()
    PKG_VERSION = auto()


class GitRepoType(Enum):
    NONE = auto()
    COMMIT = auto()
    TAG = auto()


@dataclass
class PythonProject:
    path: Path
    project_slug: str | None
    git_repo_type: GitRepoType = field(default=GitRepoType.NONE, kw_only=True)
    disallow_subprocess: DisallowCallable

    def __post_init__(self) -> None:
        self._git_setup()

    @cached_property
    def package_name(self) -> str:
        pyproject = self.path / "pyproject.toml"
        pyproject_data = tomllib.loads(pyproject.read_text())
        project_name = pyproject_data["project"]["name"]
        return project_name.lower()

    def get_version(self, version_approach: VersionApproach) -> str:
        if version_approach == VersionApproach.IMPORTLIB_METADATA:
            code = (
                "from importlib.metadata import version as v;"
                f' print(v("{self.package_name}"))'
            )
        elif version_approach == VersionApproach.PKG_VERSION:
            package_import = self.project_slug or self.package_name
            code = f"from {package_import} import version; print(version)"
        return self._run(
            ["uv", "run", "python", "-c", code], capture_output=True
        ).stdout.strip()

    def _git_setup(self) -> None:
        if self.git_repo_type == GitRepoType.NONE:
            return
        cmds = [
            ["git", "init"],
            ["git", "add", "."],
            ["git", "commit", "-n", "-m", "Create test project from template"],
        ]
        if self.git_repo_type == GitRepoType.TAG:
            cmds.append(["git", "tag", "v0.11.38", "@"])
        for cmd in cmds:
            self._run(cmd)

    def _run(
        self, args: Sequence[str], **kwargs: Any
    ) -> subprocess.CompletedProcess[str]:
        with self.disallow_subprocess.pause():
            return subprocess.run(  # noqa: S603
                args, cwd=self.path, check=True, text=True, **kwargs
            )


@pytest.fixture(
    params=[pytest.param(gr, id=gr.name.lower()) for gr in GitRepoType]
)
def git_repo_type(request: pytest.FixtureRequest) -> GitRepoType:
    return request.param


@pytest.fixture
def python_project(
    render_template: Callable[..., Path],
    project_slug: str | None,
    disallow_subprocess: DisallowCallable,
    git_repo_type: GitRepoType,
) -> PythonProject:
    return PythonProject(
        path=render_template(),
        project_slug=project_slug,
        disallow_subprocess=disallow_subprocess,
        git_repo_type=git_repo_type,
    )


@pytest.mark.parametrize(
    "version_approach",
    [pytest.param(va, id=va.name.lower()) for va in VersionApproach],
)
def test_package_version(
    python_project: PythonProject,
    version_approach: VersionApproach,
    git_repo_type: GitRepoType,
) -> None:
    version = python_project.get_version(version_approach)
    if git_repo_type == GitRepoType.NONE:
        assert version == "0.0.0"
    elif git_repo_type == GitRepoType.COMMIT:
        assert version.startswith("0.0.0.post1.dev0+")
    elif git_repo_type == GitRepoType.TAG:
        assert version == "0.11.38"
