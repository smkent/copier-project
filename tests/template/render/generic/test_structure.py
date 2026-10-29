from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest

from tests.template.utils import StructureTestCase, template

if TYPE_CHECKING:
    from tests.template.utils import StructureTest

PYTHON_ONLY_PATHS = {
    ".dockerignore",
    ".github/workflows/audit.yaml",
    ".github/workflows/release.yaml",
    "Dockerfile",
    "compose.yaml",
    "docs",
    "py.typed",
    "pyproject.toml",
    "tests",
    "zensical.toml",
}


@pytest.mark.parametrize("project_type", template.choices.project_type)
@pytest.mark.parametrize(
    "project_visibility", template.choices.project_visibility
)
def test_structure(
    structure_test: StructureTest,
    project_type: str,
    project_visibility: str,
) -> None:
    case = StructureTestCase(
        extra_data={
            "project_type": project_type,
            "project_visibility": project_visibility,
        },
        expected_present={
            ".copier-answers.yml",
            ".gitignore",
            ".pre-commit-config.yaml",
            "AGENTS.md",
            "README.md",
            "mise.toml",
            "renovate.json",
        },
        expected_absent={"common", *PYTHON_ONLY_PATHS},
    )
    case.expect_if(
        project_visibility == "public",
        ".github/workflows/ci.yaml",
        "CONTRIBUTING.md",
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
