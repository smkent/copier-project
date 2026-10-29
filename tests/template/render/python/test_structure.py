from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import pytest

from tests.template.utils import template

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


@dataclass
class StructureTestCase:
    extra_data: dict[str, Any] = field(default_factory=dict)
    expected_present: set[str] = field(default_factory=set)
    expected_absent: set[str] = field(default_factory=set)

    def expect_if(self, present: bool, *items: str) -> None:  # noqa: FBT001
        if present:
            self.expected_present |= set(items)
        else:
            self.expected_absent |= set(items)

    def run(self, render_template: Callable[..., Path]) -> None:
        rendered = render_template(**self.extra_data)
        for path in self.expected_present:
            assert (rendered / path).exists(), f"{path!r} should exist"
        for path in self.expected_absent:
            assert not (rendered / path).exists(), f"{path!r} should be absent"


@dataclass
class StructureTest:
    render_template: Callable[..., Path] = field(repr=False)

    def __call__(self, case: StructureTestCase) -> None:
        case.run(self.render_template)


@pytest.fixture
def structure_test(
    render_template: Callable[..., Path],
) -> StructureTest:
    return StructureTest(render_template=render_template)


@pytest.mark.parametrize("project_type", template.choices.project_type)
@pytest.mark.parametrize(
    "project_visibility", template.choices.project_visibility
)
@pytest.mark.parametrize(
    "enable_coverage",
    [pytest.param(True, id="coverage"), pytest.param(False, id="no_coverage")],
)
@pytest.mark.parametrize(
    "enable_pypi",
    [pytest.param(True, id="pypi"), pytest.param(False, id="no_pypi")],
)
@pytest.mark.parametrize(
    "enable_container",
    [
        pytest.param(True, id="container"),
        pytest.param(False, id="no_container"),
    ],
)
@pytest.mark.parametrize(
    "enable_docs",
    [pytest.param(True, id="docs"), pytest.param(False, id="no_docs")],
)
def test_structure(
    structure_test: StructureTest,
    project_type: str,
    project_visibility: str,
    *,
    enable_coverage: bool,
    enable_pypi: bool,
    enable_container: bool,
    enable_docs: bool,
) -> None:
    case = StructureTestCase(
        extra_data={
            "project_type": project_type,
            "project_visibility": project_visibility,
            "enable_container": enable_container,
            "enable_coverage": enable_coverage,
            "enable_pypi": enable_pypi,
            "enable_docs": enable_docs,
        },
        expected_present={
            ".gitignore",
            ".pre-commit-config.yaml",
            "README.md",
            "pyproject.toml",
            "renovate.json",
        },
    )
    case.expect_if(
        project_visibility == "public",
        ".github/workflows/audit.yaml",
        ".github/workflows/ci.yaml",
        "CONTRIBUTING.md",
    )
    case.expect_if(
        project_visibility == "public" and enable_pypi,
        ".github/workflows/release.yaml",
    )
    case.expect_if(
        enable_container,
        "Dockerfile",
        ".dockerignore",
    )
    case.expect_if(
        project_visibility == "public" and enable_container,
        ".github/workflows/container.yaml",
        ".github/workflows/ghcr.yaml",
    )
    case.expect_if(
        enable_docs,
        "docs",
        "docs/api.md",
        "docs/contributing.md",
        "docs/development/requirements.md",
        "docs/development/updates.md",
        "docs/development/workflow.md",
        "docs/index.md",
        "docs/license.md",
        "zensical.toml",
    )
    case.expect_if(
        project_visibility == "public" and enable_docs,
        ".github/workflows/docs.yaml",
        "docs/setup.md",
        "docs/releasing.md",
    )
    case.expect_if(
        project_type == "application" and enable_container, "compose.yaml"
    )
    structure_test(case)


@pytest.mark.parametrize(
    "copyright_license", template.choices.copyright_license
)
def test_structure_license(
    structure_test: StructureTest,
    copyright_license: str,
) -> None:
    case = StructureTestCase(
        extra_data={"copyright_license": copyright_license}
    )
    case.expect_if(not re.match(r"^[AL]?GPL-", copyright_license), "LICENSE")
    case.expect_if(bool(re.match(r"^[AL]?GPL-", copyright_license)), "COPYING")
    case.expect_if(
        bool(re.match(r"^LGPL-", copyright_license)), "COPYING.LESSER"
    )
    structure_test(case)


@pytest.mark.parametrize(
    "llm_contribution_policy", template.choices.llm_contribution_policy
)
@pytest.mark.parametrize(
    "project_visibility", template.choices.project_visibility
)
def test_structure_contributing(
    structure_test: StructureTest,
    project_visibility: str,
    llm_contribution_policy: str,
) -> None:
    case = StructureTestCase(
        extra_data={
            "project_visibility": project_visibility,
            "llm_contribution_policy": llm_contribution_policy,
        }
    )
    case.expect_if(project_visibility == "public", "CONTRIBUTING.md")
    if llm_contribution_policy == "accepted":
        case.expected_absent |= {
            ".github/commit-check.toml",
            "commit-check.toml",
        }
    else:
        case.expect_if(
            project_visibility == "public", ".github/commit-check.toml"
        )
        case.expect_if(project_visibility == "private", "commit-check.toml")
    structure_test(case)
