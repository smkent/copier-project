from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import yaml

from tests.template.utils import template

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


@pytest.fixture
def template_variant() -> str:
    return "python"


@pytest.mark.parametrize("project_type", template.choices.project_type)
def test_license_default(
    render_template: Callable[..., Path], project_type: str
) -> None:
    rendered = render_template(
        copyright_license=None, project_type=project_type
    )
    answers = yaml.safe_load((rendered / ".copier-answers.yml").read_text())
    assert answers["copyright_license"] == (
        "LGPL-3.0-only" if project_type == "library" else "GPL-3.0-only"
    )


@pytest.mark.parametrize(
    "copyright_license", template.choices.copyright_license
)
def test_license_choices_have_templates(copyright_license: str) -> None:
    assert (template.dir / "common" / "licenses" / copyright_license).is_file()


@pytest.mark.parametrize(
    ("previous_license", "expected_license"),
    [
        ("AGPL-3.0", "AGPL-3.0-only"),
        ("GPL-3.0", "GPL-3.0-only"),
        ("LGPL-3.0", "LGPL-3.0-only"),
        ("GPL-3.0-or-later", "GPL-3.0-or-later"),
        ("MIT", "MIT"),
    ],
)
def test_license_previous_answer(
    render_template: Callable[..., Path],
    previous_license: str,
    expected_license: str,
) -> None:
    rendered = render_template(
        copyright_license=None,
        previous_answers={
            "copyright_license": previous_license,
            "template_attribution": False,
        },
    )
    answers = yaml.safe_load((rendered / ".copier-answers.yml").read_text())
    assert answers["copyright_license"] == expected_license
    assert (
        f'license = "{expected_license}"'
        in (rendered / "pyproject.toml").read_text()
    )
