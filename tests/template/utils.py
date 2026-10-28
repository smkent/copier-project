from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any

import yaml

if TYPE_CHECKING:
    from collections.abc import Sequence


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


class Template:
    @cached_property
    def dir(self) -> Path:
        return Path(__file__).parent.parent.parent

    @cached_property
    def config(self) -> dict[str, Any]:
        return yaml.safe_load((self.dir / "copier.yaml").read_text())

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
