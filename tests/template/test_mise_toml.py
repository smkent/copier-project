"""Snapshot tests for mise.toml template."""

from collections.abc import Callable
from pathlib import Path

import pytest
from syrupy.assertion import SnapshotAssertion

from tests.utils import template


@pytest.mark.parametrize(
    "project_visibility", template.choices.project_visibility
)
@pytest.mark.parametrize(
    "enable_docs",
    [pytest.param(True, id="docs"), pytest.param(False, id="no_docs")],
)
@pytest.mark.parametrize(
    "enable_syrupy",
    [pytest.param(True, id="syrupy"), pytest.param(False, id="no_syrupy")],
)
@pytest.mark.parametrize(
    "enable_xdist",
    [pytest.param(True, id="xdist"), pytest.param(False, id="no_xdist")],
)
def test_mise_toml_features(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    *,
    project_visibility: bool,
    enable_docs: bool,
    enable_syrupy: bool,
    enable_xdist: bool,
) -> None:
    rendered = render_template(
        project_visibility=project_visibility,
        enable_docs=enable_docs,
        enable_features=[
            *(["syrupy"] if enable_syrupy else []),
            *(["xdist"] if enable_xdist else []),
        ],
    )
    assert (rendered / "mise.toml").read_text() == snapshot
