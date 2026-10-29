from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.template.utils import template

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from syrupy.assertion import SnapshotAssertion


@pytest.mark.parametrize(
    "copyright_license", template.choices.copyright_license
)
def test_license(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    copyright_license: str,
) -> None:
    rendered = render_template(copyright_license=copyright_license)
    for name in ["LICENSE", "COPYING.LESSER", "COPYING"]:
        if (rendered / name).exists():
            assert (rendered / name).read_text() == snapshot
