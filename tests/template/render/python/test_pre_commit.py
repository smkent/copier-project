from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.template.utils import template

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from syrupy.assertion import SnapshotAssertion


@template.parameterize("project_visibility", "llm_contribution_policy")
@pytest.mark.parametrize(
    "enable_syrupy",
    [pytest.param(True, id="syrupy"), pytest.param(False, id="no_syrupy")],
)
def test_pre_commit_config(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    project_visibility: str,
    llm_contribution_policy: str,
    *,
    enable_syrupy: bool,
) -> None:
    rendered = render_template(
        project_visibility=project_visibility,
        llm_contribution_policy=llm_contribution_policy,
        enable_features=[*(["syrupy"] if enable_syrupy else []), "xdist"],
    )
    assert (rendered / ".pre-commit-config.yaml").read_text() == snapshot
