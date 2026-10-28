from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable, Generator

    from tests.utils import DisallowCallable


@pytest.fixture(scope="module")
def rendered_template(
    session_render_template: Callable[..., Path],
    disallow_subprocess: DisallowCallable,
) -> Generator[Path]:
    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)
        rendered = session_render_template(
            tmp_path=tmp_path,
            enable_container=True,
            enable_coverage=True,
            enable_docs=True,
            enable_pypi=True,
        )
        with disallow_subprocess.pause():
            subprocess.run(["mise", "run", "init"], cwd=rendered, check=True)
        yield rendered
