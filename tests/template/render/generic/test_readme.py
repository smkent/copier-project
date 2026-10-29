from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.template.utils import template

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from syrupy.assertion import SnapshotAssertion


@pytest.mark.parametrize(
    "template_attribution",
    [
        pytest.param(True, id="attribution"),
        pytest.param(False, id="no_attribution"),
    ],
)
def test_readme_features(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    *,
    template_attribution: bool,
) -> None:
    rendered = render_template(template_attribution=template_attribution)
    assert (rendered / "README.md").read_text() == snapshot


@pytest.mark.parametrize(
    "project_visibility", template.choices.project_visibility
)
@pytest.mark.parametrize(
    "copyright_license", template.choices.copyright_license
)
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
