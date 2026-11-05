from __future__ import annotations

import tomllib
from typing import TYPE_CHECKING

import pytest

from tests.template.utils import template

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from syrupy.assertion import SnapshotAssertion


@pytest.mark.parametrize(
    "python_version_minimum", template.python_versions.min_param
)
@pytest.mark.parametrize(
    "python_version_maximum", template.python_versions.max_param
)
def test_dockerfile(
    render_template: Callable[..., Path],
    snapshot: SnapshotAssertion,
    *,
    python_version_minimum: str,
    python_version_maximum: str,
) -> None:
    rendered = render_template(
        project_visibility="public",
        enable_container=True,
        python_version_minimum=python_version_minimum,
        python_version_maximum=python_version_maximum,
    )
    assert (rendered / "Dockerfile").read_text() == snapshot


@pytest.mark.parametrize(
    "copyright_license", template.choices.copyright_license
)
def test_container_license(
    render_template: Callable[..., Path], copyright_license: str
) -> None:
    rendered = render_template(
        project_visibility="public",
        enable_container=True,
        copyright_license=copyright_license,
    )
    dockerfile = (rendered / "Dockerfile").read_text()
    workflow = (rendered / ".github/workflows/container.yaml").read_text()
    pyproject = tomllib.loads((rendered / "pyproject.toml").read_text())
    license_files = pyproject["project"]["license-files"]

    assert all((rendered / name).is_file() for name in license_files)
    assert f"\nCOPY README.md {' '.join(license_files)} .\n" in dockerfile
    label = "org.opencontainers.image.licenses"
    assert f'LABEL {label}="{copyright_license}"\n' in dockerfile
    assert f"{label}={copyright_license}\n" in workflow
