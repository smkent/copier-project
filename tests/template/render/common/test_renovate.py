from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from syrupy.assertion import SnapshotAssertion


def test_renovate(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
) -> None:
    rendered = render_template()
    assert (rendered / "renovate.json").read_text() == snapshot
