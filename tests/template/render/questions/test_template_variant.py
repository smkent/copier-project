from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
import yaml

from tests.template.utils import template

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


@pytest.mark.parametrize(
    ("previous_answers", "expected"),
    [
        pytest.param(None, "generic", id="new_project_default"),
        pytest.param(
            {
                "python_version_minimum": (
                    f"3.{template.python_versions.min_param}"
                )
            },
            "python",
            id="existing_unanswered_python",
        ),
        pytest.param(
            {"template_variant": "python"},
            "python",
            id="answered_python",
        ),
        pytest.param(
            {
                "template_variant": "generic",
                "python_version_minimum": (
                    f"3.{template.python_versions.min_param}"
                ),
            },
            "generic",
            id="answered_generic",
        ),
    ],
)
def test_template_variant_default(
    render_template_common: Callable[..., Path],
    previous_answers: dict[str, Any] | None,
    expected: str,
) -> None:
    rendered = render_template_common(previous_answers=previous_answers)
    answers = yaml.safe_load((rendered / ".copier-answers.yml").read_text())
    assert answers["template_variant"] == expected
