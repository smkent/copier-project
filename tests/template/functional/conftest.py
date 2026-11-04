from __future__ import annotations

import tempfile
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from tests.template.utils import template

from .mise_env import MiseEnv, MiseManager

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

    from tests.utils import DisallowCallable


TEMPLATE_VARIANT_DATA: dict[str, dict[str, Any]] = {
    "python": {
        "enable_container": True,
        "enable_coverage": True,
        "enable_docs": True,
        "enable_pypi": True,
    },
}


@pytest.fixture(scope="package", params=template.choices.template_variant)
def template_variant(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture(scope="module", params=template.choices.project_visibility)
def project_visibility(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture(scope="module")
def template_variant_args(template_variant: str) -> dict[str, str]:
    return TEMPLATE_VARIANT_DATA.get(template_variant, {}) or {}


@pytest.fixture(scope="module")
def template_args(
    template_variant: str,
    template_variant_args: dict[str, str],
    project_visibility: str,
) -> dict[str, Any]:
    return {
        "template_variant": template_variant,
        "project_visibility": project_visibility,
        **template_variant_args,
    }


@pytest.fixture(scope="package")
def mise_min_version(
    base_render_template: Callable[..., Path],
    tmp_path_factory: pytest.TempPathFactory,
) -> str:
    project = base_render_template(tmp_path=tmp_path_factory.mktemp("mise"))
    return tomllib.loads((project / "mise.toml").read_text())["min_version"]


@pytest.fixture(scope="module", params=["current"])
def mise_release(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture(scope="package")
def mise_manager(
    request: pytest.FixtureRequest,
    disallow_subprocess: DisallowCallable,
    mise_min_version: str,
) -> MiseManager:
    return MiseManager(
        request=request,
        disallow_subprocess=disallow_subprocess,
        min_version=mise_min_version,
    )


@pytest.fixture(scope="module")
def mise_env(mise_manager: MiseManager, mise_release: str) -> MiseEnv:
    return getattr(mise_manager, f"mise_{mise_release}")


@pytest.fixture(scope="module")
def rendered_project(
    base_render_template: Callable[..., Path],
    template_args: dict[str, str] | None,
    mise_env: MiseEnv,
) -> Iterator[Path]:
    with tempfile.TemporaryDirectory() as td:
        rendered = base_render_template(
            tmp_path=Path(td), **(template_args or {})
        )
        init_task_file = rendered / ".mise" / "conf.d" / "init.toml"
        assert init_task_file.is_file()
        mise_env.run(["mise", "run", "init"], cwd=rendered)
        assert not init_task_file.is_file()
        yield rendered
