from __future__ import annotations

import subprocess
import warnings
from functools import partial
from typing import TYPE_CHECKING, Any

import copier
import pytest
import yaml

from copier_project.__main__ import setup_env
from tests.template.utils import StructureTest, template
from tests.utils import DisallowCallable

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from pathlib import Path

DEFAULT_DATA: dict[str, Any] = {
    "project_name": "PKFire",
    "project_description": "Onett Little League",
    "user_name": "Ness",
    "user_email": "ness@onett.example.com",
    "github_user": "ness",
    "copyright_holder": "Ness",
    "copyright_year": "1995",
    "copyright_license": "MIT",
}


@pytest.fixture(scope="session", autouse=True)
def ensure_env() -> None:
    setup_env()


@pytest.fixture(autouse=True, scope="session")
def disallow_subprocess(
    request: pytest.FixtureRequest,
) -> Iterator[DisallowCallable]:
    with DisallowCallable(request, subprocess.Popen, "__init__")() as mock:
        yield mock


@pytest.fixture(scope="session")
def allow_subprocess(disallow_subprocess: DisallowCallable) -> Iterator[None]:
    with disallow_subprocess.pause():
        yield


@pytest.fixture(scope="session")
def session_render_template(
    disallow_subprocess: DisallowCallable,
) -> Callable[..., Path]:
    def _render(
        *,
        tmp_path: Path,
        vcs_ref: str = "HEAD",
        previous_answers: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Path:
        worktree = tmp_path / "project"
        if previous_answers is not None:
            worktree.mkdir(parents=True, exist_ok=True)
            (worktree / ".copier-answers.yml").write_text(
                yaml.safe_dump(previous_answers)
            )
        data = {
            k: v
            for k, v in {**DEFAULT_DATA, **(kwargs or {})}.items()
            if v is not None
        }
        if data.get("project_visibility") == "private":
            data.pop("github_user", None)
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                category=copier.errors.DirtyLocalWarning,
            )
            with disallow_subprocess.pause():
                copier.run_copy(
                    src_path=str(template.dir),
                    dst_path=str(worktree),
                    data=data,
                    vcs_ref=vcs_ref,
                    defaults=True,
                    overwrite=True,
                    unsafe=False,
                )
        return worktree

    return _render


@pytest.fixture
def render_template_common(
    session_render_template: Callable[..., Path], tmp_path: Path
) -> Callable[..., Path]:
    return partial(session_render_template, tmp_path=tmp_path)


@pytest.fixture
def template_variant() -> str:
    raise NotImplementedError


@pytest.fixture
def render_template(
    render_template_common: Callable[..., Path], template_variant: str
) -> Callable[..., Path]:
    return partial(render_template_common, template_variant=template_variant)


@pytest.fixture
def structure_test(
    render_template: Callable[..., Path],
) -> StructureTest:
    return StructureTest(render_template=render_template)
