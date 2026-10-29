from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.template.utils import template

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from syrupy.assertion import SnapshotAssertion


@pytest.mark.parametrize(
    "project_visibility", template.choices.project_visibility
)
@pytest.mark.parametrize(
    "python_version_minimum", template.python_versions.min_param_full_range
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
def test_pyproject_features(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    *,
    project_visibility: bool,
    python_version_minimum: str,
    enable_docs: bool,
    enable_syrupy: bool,
    enable_xdist: bool,
) -> None:
    rendered = render_template(
        project_visibility=project_visibility,
        python_version_minimum=python_version_minimum,
        enable_docs=enable_docs,
        enable_features=[
            *(["syrupy"] if enable_syrupy else []),
            *(["xdist"] if enable_xdist else []),
        ],
    )
    assert (rendered / "pyproject.toml").read_text() == snapshot


@pytest.mark.parametrize(
    "python_version_minimum", template.python_versions.min_param
)
@pytest.mark.parametrize(
    "python_version_maximum", template.python_versions.max_param
)
def test_pyproject_versions(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    *,
    python_version_minimum: str,
    python_version_maximum: str,
) -> None:
    rendered = render_template(
        python_version_minimum=python_version_minimum,
        python_version_maximum=python_version_maximum,
    )
    assert (rendered / "pyproject.toml").read_text() == snapshot


@pytest.mark.parametrize(
    "copyright_license", template.choices.copyright_license
)
def test_pyproject_licenses(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    *,
    copyright_license: str,
) -> None:
    rendered = render_template(copyright_license=copyright_license)
    assert (rendered / "pyproject.toml").read_text() == snapshot
