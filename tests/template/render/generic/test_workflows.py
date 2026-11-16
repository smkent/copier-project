from __future__ import annotations

from typing import TYPE_CHECKING

from tests.template.utils import template

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from syrupy.assertion import SnapshotAssertion


@template.parameterize("llm_contribution_policy")
def test_workflows_ci(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    llm_contribution_policy: str,
) -> None:
    rendered = render_template(
        project_visibility="public",
        llm_contribution_policy=llm_contribution_policy,
    )
    assert (
        rendered / ".github" / "workflows" / "ci.yaml"
    ).read_text() == snapshot


@template.parameterize("project_type")
def test_workflows_docs(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    project_type: str,
) -> None:
    rendered = render_template(
        project_type=project_type,
        project_visibility="public",
        enable_docs=True,
    )
    assert (
        rendered / ".github" / "workflows" / "docs.yaml"
    ).read_text() == snapshot
