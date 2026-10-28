from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.usefixtures("allow_subprocess")
def test_task_lt_lint_test(
    rendered_template: Path,
) -> None:
    subprocess.run(["mise", "run", "lt"], cwd=rendered_template, check=True)
