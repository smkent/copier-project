from __future__ import annotations

from typing import TYPE_CHECKING

from tests.template.utils import template

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from syrupy.assertion import SnapshotAssertion


@template.parameterize(
    "enable_coverage", "enable_pypi", "template_attribution"
)
def test_readme_features(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    *,
    enable_coverage: bool,
    enable_pypi: bool,
    template_attribution: bool,
) -> None:
    rendered = render_template(
        enable_coverage=enable_coverage,
        enable_pypi=enable_pypi,
        template_attribution=template_attribution,
    )
    assert (rendered / "README.md").read_text() == snapshot


@template.parameterize("project_visibility", "copyright_license")
def test_readme_project_visibility(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    project_visibility: str,
    copyright_license: str,
) -> None:
    rendered = render_template(
        project_visibility=project_visibility,
        copyright_license=copyright_license,
    )
    assert (rendered / "README.md").read_text() == snapshot


@template.parameterize("project_type")
def test_readme_project_type(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    project_type: str,
) -> None:
    rendered = render_template(project_type=project_type)
    assert (rendered / "README.md").read_text() == snapshot
