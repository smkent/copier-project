from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.template.utils import template

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from syrupy.assertion import SnapshotAssertion


def test_docs_basic(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
) -> None:
    rendered = render_template(project_visibility="public", enable_docs=True)
    for doc_file in ["index.md", "contributing.md", "license.md"]:
        assert (rendered / "docs" / doc_file).read_text() == snapshot


@pytest.mark.parametrize(
    "enable_pypi",
    [pytest.param(True, id="pypi"), pytest.param(False, id="no_pypi")],
)
@pytest.mark.parametrize(
    "enable_container",
    [
        pytest.param(True, id="container"),
        pytest.param(False, id="no_container"),
    ],
)
def test_docs_features(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    *,
    enable_container: bool,
    enable_pypi: bool,
) -> None:
    rendered = render_template(
        project_visibility="public",
        enable_container=enable_container,
        enable_pypi=enable_pypi,
        enable_docs=True,
    )
    for doc_file in ["setup.md", "releasing.md"]:
        assert (rendered / "docs" / doc_file).read_text() == snapshot


@pytest.mark.parametrize(
    "project_visibility", template.choices.project_visibility
)
@pytest.mark.parametrize(
    "enable_pypi",
    [pytest.param(True, id="pypi"), pytest.param(False, id="no_pypi")],
)
@pytest.mark.parametrize(
    "enable_syrupy",
    [pytest.param(True, id="syrupy"), pytest.param(False, id="no_syrupy")],
)
def test_docs_development_features(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    *,
    project_visibility: str,
    enable_pypi: bool,
    enable_syrupy: bool,
) -> None:
    rendered = render_template(
        project_visibility=project_visibility,
        enable_pypi=enable_pypi,
        enable_docs=True,
        enable_features=["syrupy"] if enable_syrupy else [],
    )
    for doc_file in ["requirements.md", "workflow.md", "updates.md"]:
        assert (
            rendered / "docs" / "development" / doc_file
        ).read_text() == snapshot


@pytest.mark.parametrize(
    "copyright_license", template.choices.copyright_license
)
def test_docs_license(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    copyright_license: str,
) -> None:
    rendered = render_template(
        enable_docs=True, copyright_license=copyright_license
    )
    assert (rendered / "docs" / "license.md").read_text() == snapshot
