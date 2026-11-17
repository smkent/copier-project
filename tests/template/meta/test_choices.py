from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
import yaml

from tests.template.utils import Template

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path


@pytest.mark.parametrize(
    ("question_name", "config", "expected_params"),
    [
        pytest.param(
            "moon",
            {
                "type": "bool",
                "qmark": "🌕",
                "help": "Is that a moon?",
                "default": False,
            },
            [
                pytest.param(True, id="moon"),
                pytest.param(False, id="no-moon"),
            ],
            id="bool",
        ),
        pytest.param(
            "grit_enabled",
            {
                "type": "yaml",
                "qmark": "🌕",
                "help": "Enable local grit?",
                "default": True,
                "choices": {
                    "Enabled, default": True,
                    "Enabled, scum and villainy": "scum_villainy",
                    "Disabled": False,
                },
            },
            [
                pytest.param(True, id="grit_enabled"),
                pytest.param("scum_villainy", id="scum_villainy"),
                pytest.param(False, id="no-grit_enabled"),
            ],
            id="mixed_yaml",
        ),
        pytest.param(
            "starship",
            {
                "type": "str",
                "qmark": "🚀",
                "help": "Starship",
                "default": 7,
                "choices": {
                    "Nothing": "",
                    "A-Wing": "a-wing",
                    "B-Wing": "b-wing",
                    "X-Wing": "x-wing",
                    "Y-Wing": "y-wing",
                    "CR90 Corvette": "cr90-corvette",
                    "Millennium Falcon": "millennium-falcon",
                },
            },
            [
                pytest.param("", id="nothing"),
                *[
                    pytest.param(value, id=value)
                    for value in [
                        "a-wing",
                        "b-wing",
                        "x-wing",
                        "y-wing",
                        "cr90-corvette",
                        "millennium-falcon",
                    ]
                ],
            ],
            id="str",
        ),
    ],
)
def test_choices(
    copier_yaml: Path,
    question_name: str,
    config: dict[str, Any],
    expected_params: Sequence[Any],
) -> None:
    with copier_yaml.open("w") as file:
        yaml.safe_dump({question_name: config}, stream=file, sort_keys=False)
    assert (
        getattr(Template(copier_yaml.parent).choices, question_name)
        == expected_params
    )
