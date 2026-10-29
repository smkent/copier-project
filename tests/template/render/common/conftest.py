from __future__ import annotations

import pytest

from tests.template.utils import template


@pytest.fixture(params=template.choices.template_variant)
def template_variant(request: pytest.FixtureRequest) -> str:
    return request.param
