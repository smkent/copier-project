from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.utils import template

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from syrupy.assertion import SnapshotAssertion


@pytest.mark.parametrize(
    "project_visibility", template.choices.project_visibility
)
def test_compose_features(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    project_visibility: str,
) -> None:
    rendered = render_template(
        project_type="application",
        project_visibility=project_visibility,
        enable_container=True,
    )
    assert (rendered / "compose.yaml").read_text() == snapshot
