"""Snapshot tests for compose.yaml template."""

from collections.abc import Callable
from pathlib import Path

import pytest
from syrupy.assertion import SnapshotAssertion

from tests.utils import template


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
