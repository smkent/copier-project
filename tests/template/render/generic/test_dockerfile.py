from __future__ import annotations

from typing import TYPE_CHECKING

from tests.template.utils import template

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from syrupy.assertion import SnapshotAssertion


@template.parameterize("copyright_license")
def test_dockerfile(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    copyright_license: str,
) -> None:
    rendered = render_template(
        project_visibility="public",
        copyright_license=copyright_license,
        enable_container=True,
    )
    assert (rendered / "Dockerfile").read_text() == snapshot
