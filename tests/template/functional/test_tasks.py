from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from .mise_env import MiseEnv


@pytest.mark.usefixtures("allow_subprocess")
def test_task_lt_lint_test(rendered_template: Path, mise_env: MiseEnv) -> None:
    mise_env.run(["mise", "run", "lt"], cwd=rendered_template)
