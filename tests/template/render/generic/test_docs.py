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


def test_docs_features(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
) -> None:
    rendered = render_template(project_visibility="public", enable_docs=True)
    for doc_file in ["setup.md"]:
        assert (rendered / "docs" / doc_file).read_text() == snapshot


@pytest.mark.parametrize(
    "project_visibility", template.choices.project_visibility
)
def test_docs_development_features(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    *,
    project_visibility: str,
) -> None:
    rendered = render_template(
        project_visibility=project_visibility,
        enable_docs=True,
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
