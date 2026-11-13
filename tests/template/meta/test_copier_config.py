from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.template.utils import Template

if TYPE_CHECKING:
    from pathlib import Path


def test_copier_config_include(copier_yaml: Path) -> None:
    copier_yaml.write_text("a: 1\n---\n!include more.yaml\n")
    (copier_yaml.parent / "more.yaml").write_text("b: 2\n---\nc: 3\n")
    config = Template(copier_yaml.parent).config
    assert config == {"a": 1, "b": 2, "c": 3}


def test_copier_config_duplicate_keys(copier_yaml: Path) -> None:
    copier_yaml.write_text("a: 1\n---\n!include more.yaml\n")
    (copier_yaml.parent / "more.yaml").write_text("a: 2\n---\nb: 3\n")
    with pytest.raises(ValueError, match="Duplicate keys"):
        assert Template(copier_yaml.parent).config
