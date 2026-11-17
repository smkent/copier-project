from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from syrupy.assertion import SnapshotAssertion


def test_release_yaml(
    render_template: Callable[..., Path], snapshot: SnapshotAssertion
) -> None:
    rendered = render_template(project_visibility="public", enable_pypi=True)
    assert (rendered / ".github" / "release.yaml").read_text() == snapshot
