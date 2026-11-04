from __future__ import annotations

import subprocess
import tomllib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from tests.utils import DisallowCallable


def test_package_version(
    disallow_subprocess: DisallowCallable, render_template: Callable[..., Path]
) -> None:
    rendered = render_template()
    pyproject = rendered / "pyproject.toml"
    pyproject_data = tomllib.loads(pyproject.read_text())
    project_name = pyproject_data["project"]["name"]
    pkg_import = project_name.lower()
    code = (
        f"from importlib.metadata import version as v;"
        f' print(v("{pkg_import}"))'
    )
    cmd = ["uv", "run", "python", "-c", code]
    with disallow_subprocess.pause():
        version = subprocess.run(  # noqa: S603
            cmd,
            cwd=rendered,
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()
    assert version == "0.0.0"
