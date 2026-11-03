from __future__ import annotations

import json
import os
import shutil
import subprocess
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator, Sequence

    from tests.utils import DisallowCallable


@dataclass(frozen=True)
class MiseManager:
    ENV_REMOVE_PREFIXES = ("GIT_CONFIG", "MISE_", "__MISE_", "XDG_")
    MISE_TOOL = "aqua:jdx/mise"

    request: pytest.FixtureRequest
    disallow_subprocess: DisallowCallable
    min_version: str

    def __post_init__(self) -> None:
        self._prune_unused_versions()

    @cached_property
    def mise_current(self) -> MiseEnv:
        return MiseEnv(manager=self, executable=self.executable)

    @cached_property
    def mise_minimum(self) -> MiseEnv:
        if self.mise_current.version == self.min_version:
            pytest.skip(f"Current mise is the minimum ({self.min_version})")
        return self._install(self.min_version)

    @cached_property
    def cache_dir(self) -> Path:
        return self.request.config.cache.mkdir("mise")

    @cached_property
    def live_data_dir(self) -> Path:
        with self.disallow_subprocess.pause():
            output = subprocess.run(  # noqa: PLW1510, S603
                [
                    self.executable,
                    "--no-config",
                    "--no-env",
                    "--no-hooks",
                    "doctor",
                    "--json",
                ],
                capture_output=True,
                text=True,
            ).stdout
        return Path(json.loads(output)["dirs"]["data"])

    @cached_property
    def executable(self) -> Path:
        if not (mise := shutil.which("mise")):
            msg = "mise not found in PATH"
            raise FileNotFoundError(msg)
        return Path(mise).resolve()

    @cached_property
    def versions_dir(self) -> Path:
        path = self.cache_dir / "versions"
        path.mkdir(exist_ok=True)
        return path

    @cached_property
    def env(self) -> dict[str, str]:
        def _uv_dir(name: str) -> Path:
            with self.disallow_subprocess.pause():
                return Path(
                    subprocess.run(  # noqa: S603
                        ["uv", name, "dir"],
                        capture_output=True,
                        check=True,
                        text=True,
                    ).stdout.strip()
                )

        base_env = {
            k: v
            for k, v in os.environ.items()
            if not k.startswith(self.ENV_REMOVE_PREFIXES)
        }
        path = os.pathsep.join(
            [
                p
                for p in os.environ.get("PATH", "").split(os.pathsep)
                if p and not Path(p).is_relative_to(self.live_data_dir)
            ]
        )
        return base_env | {
            "PATH": path,
            "GIT_CONFIG_NOSYSTEM": "1",
            "MISE_YES": "1",
            "UV_CACHE_DIR": str(_uv_dir("cache")),
            "UV_PYTHON_INSTALL_DIR": str(_uv_dir("python")),
        }

    def executable_version(self, executable: Path) -> str:
        with self.disallow_subprocess.pause():
            result = subprocess.run(  # noqa: S603
                [executable, "--version"],
                capture_output=True,
                check=True,
                text=True,
            )
        return result.stdout.split()[0]

    def _install(self, version: str) -> MiseEnv:
        tool = f"{self.MISE_TOOL}@{version}"
        self.mise_current.run(["mise", "install", tool])
        output = self.mise_current.run(
            ["mise", "bin-paths", tool], capture_output=True
        ).stdout.strip()
        return MiseEnv(manager=self, executable=Path(output) / "mise")

    def _prune_unused_versions(self) -> None:
        current_version = self.executable_version(self.executable)
        keep = {current_version, self.min_version}
        for path in self.versions_dir.iterdir():
            if path.is_dir() and path.name not in keep:
                shutil.rmtree(path, ignore_errors=True)


@dataclass(frozen=True)
class MiseEnv:
    manager: MiseManager
    executable: Path = field(repr=False)

    def __post_init__(self) -> None:
        assert (
            self.manager.executable_version(self.executable_link)
            == self.version
        )

    @cached_property
    def env(self) -> dict[str, str]:
        return self.manager.env | {
            "HOME": str(self.home),
            "PATH": os.pathsep.join(
                [str(self.executable_link.parent), self.manager.env["PATH"]]
            ),
            "MISE_SYSTEM_CONFIG_DIR": str(self.system_dir / "config"),
            "MISE_SYSTEM_INSTALLS_DIR": str(self.system_dir / "installs"),
            "MISE_SYSTEM_SHIMS_DIR": str(self.system_dir / "shims"),
        }

    @cached_property
    def version(self) -> str:
        return self.manager.executable_version(self.executable)

    @cached_property
    def root(self) -> Path:
        return self.manager.versions_dir / self.version

    @cached_property
    def home(self) -> Path:
        path = self.root / "home"
        path.mkdir(parents=True, exist_ok=True)
        # Configure git
        gitconfig = path / ".gitconfig"
        content = (
            "[init]\n"
            "defaultBranch = main\n"
            "[user]\n"
            "name = Ness\n"
            "email = ness@onett.example.com\n"
        )
        if not gitconfig.is_file() or gitconfig.read_text() != content:
            with self._replace_atomic(gitconfig) as tmp:
                tmp.write_text(content)
        return path

    @cached_property
    def executable_link(self) -> Path:
        bin_dir = self.root / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        path = bin_dir / "mise"
        if not path.is_symlink() or path.readlink() != self.executable:
            with self._replace_atomic(path) as tmp:
                tmp.unlink(missing_ok=True)
                tmp.symlink_to(self.executable)
        return path

    @cached_property
    def system_dir(self) -> Path:
        return self.root / "system"

    def run(
        self,
        args: Sequence[str],
        *,
        cwd: Path | None = None,
        check: bool = True,
        **kwargs: Any,
    ) -> subprocess.CompletedProcess[str]:
        cwd = cwd or self.root
        env = {
            **self.env,
            # Use and trust only config files in cwd
            "MISE_CEILING_PATHS": str(cwd.parent),
            "MISE_TRUSTED_CONFIG_PATHS": str(cwd),
        }
        with self.manager.disallow_subprocess.pause():
            return subprocess.run(  # noqa: S603
                args, cwd=cwd, env=env, check=check, text=True, **kwargs
            )

    @staticmethod
    @contextmanager
    def _replace_atomic(path: Path) -> Generator[Path]:
        """Temporary sibling of path, for replacing it atomically."""
        temp_path = path.with_name(f".{path.name}.{os.getpid()}")
        yield temp_path
        temp_path.replace(path)
