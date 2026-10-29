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
def test_contributing_features(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    llm_contribution_policy: str,
) -> None:
    rendered = render_template(llm_contribution_policy=llm_contribution_policy)
    assert (rendered / "CONTRIBUTING.md").read_text() == snapshot


@pytest.mark.parametrize(
    "copyright_license", template.choices.copyright_license
)
def test_contributing_license(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    copyright_license: str,
) -> None:
    rendered = render_template(copyright_license=copyright_license)
    assert (rendered / "CONTRIBUTING.md").read_text() == snapshot
