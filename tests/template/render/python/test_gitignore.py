from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.template.utils import template

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from syrupy.assertion import SnapshotAssertion


@pytest.mark.parametrize("project_type", template.choices.project_type)
@pytest.mark.parametrize(
    "project_visibility", template.choices.project_visibility
)
@pytest.mark.parametrize("enable_docs", template.choices.enable_docs)
def test_gitignore(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    project_type: str,
    project_visibility: str,
    *,
    enable_docs: bool,
) -> None:
    rendered = render_template(
        project_type=project_type,
        project_visibility=project_visibility,
        enable_docs=enable_docs,
    )
    assert (rendered / ".gitignore").read_text() == snapshot
