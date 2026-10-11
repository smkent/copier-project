from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.utils import template

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from syrupy.assertion import SnapshotAssertion


@pytest.mark.parametrize(
    "enable_coverage",
    [pytest.param(True, id="coverage"), pytest.param(False, id="no_coverage")],
)
@pytest.mark.parametrize(
    "enable_docs",
    [pytest.param(True, id="docs"), pytest.param(False, id="no_docs")],
)
def test_workflows_ci(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    *,
    enable_coverage: bool,
    enable_docs: bool,
) -> None:
    rendered = render_template(
        project_type="application",
        project_visibility="public",
        enable_coverage=enable_coverage,
        enable_docs=enable_docs,
    )
    assert (
        rendered / ".github" / "workflows" / "ci.yaml"
    ).read_text() == snapshot


@pytest.mark.parametrize(
    "python_version_minimum", template.python_versions.min_param
)
@pytest.mark.parametrize(
    "python_version_maximum", template.python_versions.max_param
)
def test_workflows_ci_versions(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    *,
    python_version_minimum: str,
    python_version_maximum: str,
) -> None:
    rendered = render_template(
        project_visibility="public",
        python_version_minimum=python_version_minimum,
        python_version_maximum=python_version_maximum,
    )
    assert (
        rendered / ".github" / "workflows" / "ci.yaml"
    ).read_text() == snapshot


def test_workflows_release(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
) -> None:
    rendered = render_template(
        project_type="application",
        project_visibility="public",
        enable_pypi=True,
    )
    assert (
        rendered / ".github" / "workflows" / "release.yaml"
    ).read_text() == snapshot
