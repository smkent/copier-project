from __future__ import annotations

from typing import TYPE_CHECKING

from tests.template.utils import template

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from syrupy.assertion import SnapshotAssertion


@template.parameterize("enable_docs", "llm_contribution_policy")
def test_contributing_features(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    llm_contribution_policy: str,
    *,
    enable_docs: bool,
) -> None:
    rendered = render_template(
        enable_docs=enable_docs,
        llm_contribution_policy=llm_contribution_policy,
    )
    assert (rendered / "CONTRIBUTING.md").read_text() == snapshot


@template.parameterize("copyright_license")
def test_contributing_license(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    copyright_license: str,
) -> None:
    rendered = render_template(copyright_license=copyright_license)
    assert (rendered / "CONTRIBUTING.md").read_text() == snapshot
