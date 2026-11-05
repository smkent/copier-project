from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

import pytest
import yaml

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from tests.utils import DisallowCallable


@pytest.fixture(scope="module")
def template_args(
    template_variant: str,
    template_variant_args: dict[str, str],
    project_slug: str | None,
) -> dict[str, str]:
    return {
        "template_variant": template_variant,
        **({"project_slug": project_slug} if project_slug is not None else {}),
        **template_variant_args,
    }


@pytest.mark.usefixtures("project_slug")
def test_package_main(
    disallow_subprocess: DisallowCallable, render_template: Callable[..., Path]
) -> None:
    rendered = render_template()
    answers = yaml.safe_load((rendered / ".copier-answers.yml").read_text())
    with disallow_subprocess.pause():
        subprocess.run(  # noqa: S603
            ["uv", "run", "python", "-m", answers["project_slug"]],
            cwd=rendered,
            check=True,
        )
