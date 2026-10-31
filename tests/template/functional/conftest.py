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
def rendered_template(
    request: pytest.FixtureRequest,
    session_render_template: Callable[..., Path],
    disallow_subprocess: DisallowCallable,
) -> Generator[Path]:
    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)
        rendered = session_render_template(
            tmp_path=tmp_path,
            template_variant=request.param,
            **(TEMPLATE_VARIANT_DATA.get(request.param) or {}),
        )
        init_task_file = rendered / ".mise" / "conf.d" / "init.toml"
        assert init_task_file.is_file()
        with disallow_subprocess.pause():
            subprocess.run(["mise", "run", "init"], cwd=rendered, check=True)
        assert not init_task_file.is_file()
        yield rendered
