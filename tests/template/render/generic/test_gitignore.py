from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from syrupy.assertion import SnapshotAssertion


@pytest.mark.parametrize(
    "enable_docs",
    [pytest.param(True, id="docs"), pytest.param(False, id="no_docs")],
)
def test_gitignore(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    *,
    enable_docs: bool,
) -> None:
    rendered = render_template(enable_docs=enable_docs)
    assert (rendered / ".gitignore").read_text() == snapshot
