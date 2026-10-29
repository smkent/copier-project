from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.template.utils import Template

if TYPE_CHECKING:
    from pathlib import Path


def test_copier_config_include(tmp_path: Path) -> None:
    (tmp_path / "copier.yaml").write_text("a: 1\n---\n!include more.yaml\n")
    (tmp_path / "more.yaml").write_text("b: 2\n---\nc: 3\n")
    config = Template(tmp_path).config
    assert config == {"a": 1, "b": 2, "c": 3}


def test_copier_config_duplicate_keys(tmp_path: Path) -> None:
    (tmp_path / "copier.yaml").write_text("a: 1\n---\n!include more.yaml\n")
    (tmp_path / "more.yaml").write_text("a: 2\n---\nb: 3\n")
    with pytest.raises(ValueError, match="Duplicate keys"):
        assert Template(tmp_path).config
