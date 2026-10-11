from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.utils import template

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from syrupy.assertion import SnapshotAssertion


@pytest.mark.parametrize(
    "project_visibility", template.choices.project_visibility
)
@pytest.mark.parametrize(
    "enable_pypi",
    [pytest.param(True, id="pypi"), pytest.param(False, id="no_pypi")],
)
def test_zensical_features(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    *,
    project_visibility: str,
    enable_pypi: bool,
) -> None:
    rendered = render_template(
        project_visibility=project_visibility,
        enable_pypi=enable_pypi,
        enable_docs=True,
    )
    assert (rendered / "zensical.toml").read_text() == snapshot


@pytest.mark.parametrize(
    ("copyright_license", "expected"),
    [
        ("MIT", 'copyright = "&copy; 1995 Ness and contributors"'),
        ("CC0-1.0", 'copyright = "Written in 1995 by Ness and contributors"'),
    ],
)
def test_zensical_copyright(
    render_template: Callable[..., Path],
    copyright_license: str,
    expected: str,
) -> None:
    rendered = render_template(
        enable_docs=True, copyright_license=copyright_license
    )
    assert expected in (rendered / "zensical.toml").read_text().splitlines()
