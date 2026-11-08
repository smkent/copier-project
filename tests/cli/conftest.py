from __future__ import annotations

import sys
from dataclasses import dataclass

import pytest

from copier_project.__main__ import main


@dataclass
class MainRunner:
    monkeypatch: pytest.MonkeyPatch

    def __call__(self, *cmd: str, match: int = 0) -> None:
        self.monkeypatch.setattr(sys, "argv", ["copier-project", *cmd])
        with pytest.raises(SystemExit, match=str(match)):
            main()


@pytest.fixture(scope="module")
def template_args() -> None:
    return None


@pytest.fixture
def main_runner(monkeypatch: pytest.MonkeyPatch) -> MainRunner:
    return MainRunner(monkeypatch=monkeypatch)
