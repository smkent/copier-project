from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any

import yaml

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence


@dataclass
class PythonVersionsSupported:
    minor_min: int
    minor_max: int

    @cached_property
    def minor_mid(self) -> int:
        return self.minor_min + round((self.minor_max - self.minor_min) / 2)

    @cached_property
    def min_param(self) -> Sequence[str]:
        return tuple(f"3.{v}" for v in (self.minor_min, self.minor_mid))

    @cached_property
    def min_param_full_range(self) -> Sequence[str]:
        return tuple(f"3.{v}" for v in (self.minor_min, self.minor_max))

    @cached_property
    def max_param(self) -> Sequence[str]:
        return (
            *(f"3.{v}" for v in (self.minor_mid, self.minor_max)),
            "No maximum",
        )


@dataclass
class StructureTestCase:
    extra_data: dict[str, Any] = field(default_factory=dict)
    expected_present: set[str] = field(
        default_factory=lambda: {
            ".copier-answers.yml",
            ".gitignore",
            ".mise/conf.d/init.toml",
            ".pre-commit-config.yaml",
            "AGENTS.md",
            "README.md",
            "mise.toml",
            "renovate.json",
        }
    )
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


@dataclass
class Template:
    dir: Path = field(default=Path(__file__).parent.parent.parent)

    @cached_property
    def config(self) -> dict[str, Any]:
        class Loader(yaml.SafeLoader):
            """Load copier.yaml with its `!include` documents merged in order.

            Duplicate keys across documents are errors.
            """

            _dir = self.dir

            def include(self, node: yaml.ScalarNode) -> list[Any]:
                include_path = self._dir / self.construct_scalar(node)
                return list(
                    yaml.load_all(include_path.read_text(), Loader=type(self))
                )

            @classmethod
            def load(cls) -> dict[str, Any]:
                config_path = cls._dir / "copier.yaml"
                config: dict[str, Any] = {}
                for doc in yaml.load_all(config_path.read_text(), Loader=cls):
                    for part in doc if isinstance(doc, list) else [doc]:
                        if dupes := config.keys() & part.keys():
                            raise ValueError(
                                f"Duplicate keys {dupes} in {config_path}"
                            )
                        config.update(part)
                return config

        Loader.add_constructor("!include", Loader.include)
        return Loader.load()

    @cached_property
    def choices(self) -> SimpleNamespace:
        return SimpleNamespace(
            **{
                k: list(choices.values())
                if isinstance(choices, dict)
                else choices
                for k, v in self.config.items()
                if isinstance(v, dict)
                and (choices := v.get("choices"))
                and isinstance(choices, (dict, list))
            }
        )

    @cached_property
    def python_versions(self) -> PythonVersionsSupported:
        python_versions_supported = self.config[
            "template_python_versions_supported"
        ]["default"]
        return PythonVersionsSupported(
            minor_min=int(python_versions_supported["min_minor"]),
            minor_max=int(python_versions_supported["max_minor"]),
        )


template = Template()
