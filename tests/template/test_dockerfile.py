from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.utils import template

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from syrupy.assertion import SnapshotAssertion


@pytest.mark.parametrize(
    "python_version_minimum", template.python_versions.min_param
)
@pytest.mark.parametrize(
    "python_version_maximum", template.python_versions.max_param
)
def test_workflows_container(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    *,
    python_version_minimum: str,
    python_version_maximum: str,
) -> None:
    rendered = render_template(
        project_visibility="public",
        enable_container=True,
        python_version_minimum=python_version_minimum,
        python_version_maximum=python_version_maximum,
    )
    assert (rendered / "Dockerfile").read_text() == snapshot
