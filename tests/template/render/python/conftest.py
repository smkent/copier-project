from __future__ import annotations

import pytest


@pytest.fixture(scope="package")
def template_variant() -> str:
    return "python"
