from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from syrupy.assertion import SnapshotAssertion


def test_bumpversion_toml(
    render_template: Callable[..., Path], snapshot: SnapshotAssertion
) -> None:
    rendered = render_template()
    assert (rendered / ".bumpversion.toml").read_text() == snapshot
