from __future__ import annotations

import traceback
from typing import TypedDict, Callable, Any


# def awesome_lang(key: str) -> Any: ...
Lang = Callable[[str], Any]


langs: dict[str, Lang] = {
    "__missing__": lambda key: f"<missing: {key}>"
}


class Config(TypedDict):
    # def get_lang(depth: int) -> str: ...
    get_lang: Callable[[int], Lang | str]
    # def on_exception() -> str: ...
    on_exception: Callable[[], str]


config = Config(
    get_lang=lambda _: "__missing__",
    on_exception=traceback.format_exc
)
