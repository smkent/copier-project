from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Self
from unittest.mock import MagicMock, patch

if TYPE_CHECKING:
    from collections.abc import Callable, Generator

    import pytest


@dataclass
class DisallowCallable:
    request: pytest.FixtureRequest
    obj: object
    attr: str
    original: Callable[..., Any] = field(init=False)
    enabled: bool = field(default=False, init=False)
    mock_attr: MagicMock | None = field(default=None, init=False)

    @dataclass
    class DisallowedError(Exception):
        mock: DisallowCallable

        def __str__(self) -> str:
            fn = self.mock.original
            name = f"{fn.__module__}." + (
                getattr(fn, "__qualname__", None)
                or getattr(fn, "__name__", "(unknown)")
            )
            return f"`{name}` disallowed via {self.mock.request.fixturename}"

    def __post_init__(self) -> None:
        self.original = getattr(self.obj, self.attr)

    @contextmanager
    def __call__(self) -> Generator[Self]:

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if self.enabled:
                return self.original(*args, **kwargs)
            raise self.DisallowedError(self)

        with patch.object(
            self.obj, self.attr, autospec=True, side_effect=wrapper
        ) as mock_attr:
            self.mock_attr = mock_attr
            yield self

    @contextmanager
    def pause(self) -> Generator[None]:
        if self.mock_attr:
            with patch.object(self.obj, self.attr, self.original):
                yield
            self.mock_attr.assert_not_called()
