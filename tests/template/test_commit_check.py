from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from syrupy.assertion import SnapshotAssertion


@pytest.mark.parametrize(
    "llm_contribution_policy", ["accepted-with-disclosure", "not-accepted"]
)
@pytest.mark.parametrize(
    ("project_visibility", "config_path"),
    [
        ("public", ".github/commit-check.toml"),
        ("private", "commit-check.toml"),
    ],
)
def test_commit_check_config(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    project_visibility: str,
    config_path: str,
    llm_contribution_policy: str,
) -> None:
    rendered = render_template(
        project_visibility=project_visibility,
        llm_contribution_policy=llm_contribution_policy,
    )
    assert (rendered / config_path).read_text() == snapshot
