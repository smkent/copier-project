from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from tests.template.utils import template

if TYPE_CHECKING:
    from collections.abc import Callable, Generator

    from tests.utils import DisallowCallable


TEMPLATE_VARIANT_DATA: dict[str, dict[str, Any]] = {
    "python": {
        "enable_container": True,
        "enable_coverage": True,
        "enable_docs": True,
        "enable_pypi": True,
    },
}


@pytest.fixture(scope="module", params=template.choices.template_variant)
def template_variant(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture(scope="module", params=template.choices.project_visibility)
def project_visibility(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture(scope="module")
def rendered_template(
    session_render_template: Callable[..., Path],
    disallow_subprocess: DisallowCallable,
    template_variant: str,
    project_visibility: str,
) -> Generator[Path]:
    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)
        rendered = session_render_template(
            tmp_path=tmp_path,
            template_variant=template_variant,
            project_visibility=project_visibility,
            **(TEMPLATE_VARIANT_DATA.get(template_variant) or {}),
        )
        init_task_file = rendered / ".mise" / "conf.d" / "init.toml"
        assert init_task_file.is_file()
        with disallow_subprocess.pause():
            subprocess.run(["mise", "run", "init"], cwd=rendered, check=True)
        assert not init_task_file.is_file()
        yield rendered
