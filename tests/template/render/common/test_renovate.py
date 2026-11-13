from __future__ import annotations

from typing import TYPE_CHECKING

from tests.template.utils import template

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from syrupy.assertion import SnapshotAssertion


@template.parameterize("dependency_cooldown")
def test_renovate(
    render_template: Callable[..., Path],
    dependency_cooldown: str,
    snapshot: SnapshotAssertion,
) -> None:
    rendered = render_template(dependency_cooldown=dependency_cooldown)
    assert (rendered / "renovate.json").read_text() == snapshot
