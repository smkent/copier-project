from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from tests.utils import DisallowCallable


def test_build_wheel(
    disallow_subprocess: DisallowCallable, render_template: Callable[..., Path]
) -> None:
    rendered = render_template()
    with disallow_subprocess.pause():
        subprocess.run(["uv", "build"], cwd=rendered, check=True)
    pkg_prefix = "pkfire-0.0.0"
    for file in [".tar.gz", "-py3-none-any.whl"]:
        assert (rendered / "dist" / f"{pkg_prefix}{file}").is_file()
