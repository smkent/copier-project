from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.template.utils import template

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from syrupy.assertion import SnapshotAssertion


@template.parameterize("project_type", "enable_coverage", "enable_docs")
def test_workflows_ci(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    project_type: str,
    *,
    enable_coverage: bool,
    enable_docs: bool,
) -> None:
    rendered = render_template(
        project_type=project_type,
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


@template.parameterize("project_type")
def test_workflows_audit(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    project_type: str,
) -> None:
    rendered = render_template(
        project_type=project_type, project_visibility="public"
    )
    assert (
        rendered / ".github" / "workflows" / "audit.yaml"
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


@template.parameterize("dependency_cooldown")
def test_workflows_container(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    dependency_cooldown: str,
) -> None:
    rendered = render_template(
        project_type="application",
        project_visibility="public",
        dependency_cooldown=dependency_cooldown,
        enable_container=True,
    )
    assert (
        rendered / ".github" / "workflows" / "container.yaml"
    ).read_text() == snapshot


def test_workflows_container_registry(
    render_template: Callable[..., Path], snapshot: SnapshotAssertion
) -> None:
    rendered = render_template(
        project_type="application",
        project_visibility="public",
        enable_container=True,
    )
    assert (
        rendered / ".github" / "workflows" / "ghcr.yaml"
    ).read_text() == snapshot


@template.parameterize("project_type")
def test_workflows_release(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    project_type: str,
) -> None:
    rendered = render_template(
        project_type=project_type,
        project_visibility="public",
        enable_pypi=True,
    )
    assert (
        rendered / ".github" / "workflows" / "release.yaml"
    ).read_text() == snapshot
