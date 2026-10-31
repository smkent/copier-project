from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING

import pytest

import copier_project
from copier_project.__main__ import main, version

if TYPE_CHECKING:
    from collections.abc import Generator


def test_version() -> None:
    assert copier_project.version


@pytest.fixture
def version_output(capsys: pytest.CaptureFixture[str]) -> Generator[None]:
    yield None
    capture_result = capsys.readouterr()
    assert capture_result.out == copier_project.version + os.linesep
    assert capture_result.err == ""


@pytest.mark.usefixtures("version_output")
@pytest.mark.parametrize("cli_option", ["version", "--version", "-V"])
def test_version_main(
    monkeypatch: pytest.MonkeyPatch, cli_option: str
) -> None:
    monkeypatch.setattr(sys, "argv", ["copier-project", cli_option])
    with pytest.raises(SystemExit, match=str(0)):
        main()


@pytest.mark.usefixtures("version_output")
def test_version_function() -> None:
    version()
