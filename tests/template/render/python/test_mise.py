from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.template.utils import template

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from syrupy.assertion import SnapshotAssertion


@pytest.mark.parametrize(
    "llm_contribution_policy", template.choices.llm_contribution_policy
)
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
def test_mise_config(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    *,
    project_visibility: bool,
    llm_contribution_policy: str,
    enable_docs: bool,
    enable_syrupy: bool,
    enable_xdist: bool,
) -> None:
    rendered = render_template(
        project_visibility=project_visibility,
        llm_contribution_policy=llm_contribution_policy,
        enable_docs=enable_docs,
        enable_features=[
            *(["syrupy"] if enable_syrupy else []),
            *(["xdist"] if enable_xdist else []),
        ],
    )
    for file in ["mise.toml", ".mise/conf.d/init.toml"]:
        assert (rendered / file).read_text() == snapshot
