from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from tests.template.functional.mise_env import MiseEnv


@pytest.fixture(scope="module")
def template_args(
    template_variant: str,
    template_variant_args: dict[str, str],
) -> dict[str, Any]:
    return {
        "template_variant": template_variant,
        "project_type": "application",
        **template_variant_args,
    }


def test_uv_lock(rendered_project: Path, mise_env: MiseEnv) -> None:
    mise_env.run(
        ["git", "ls-files", "--error-unmatch", "uv.lock"], cwd=rendered_project
    )
    mise_env.run(
        ["mise", "exec", "--", "uv", "sync", "--locked"], cwd=rendered_project
    )
