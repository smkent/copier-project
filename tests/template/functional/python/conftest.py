from __future__ import annotations

import pytest


@pytest.fixture(scope="package")
def template_variant() -> str:
    return "python"


@pytest.fixture(
    scope="module",
    params=[
        pytest.param(None, id="default_slug"),
        pytest.param("Custom_Slug", id="custom_slug"),
    ],
)
def project_slug(request: pytest.FixtureRequest) -> str | None:
    return request.param


@pytest.fixture(scope="module")
def template_args(
    template_variant: str,
    template_variant_args: dict[str, str],
    project_visibility: str,
    project_slug: str | None,
) -> dict[str, str]:
    return {
        "template_variant": template_variant,
        "project_visibility": project_visibility,
        **({"project_slug": project_slug} if project_slug is not None else {}),
        **template_variant_args,
    }
