from __future__ import annotations

import re
from functools import partial
from pathlib import Path
from typing import Any

import yaml

from .config import config, langs, Lang
from .utils import modulename


def load_lang(path: str | Path, encoding: str | None = None) -> dict[str, Any]:
    assert (path := Path(path)).is_file() or path.is_dir()

    if path.is_file():
        with path.open(encoding=encoding) as file:
            return yaml.safe_load(file)

    return {
        path.name: load_lang(path, encoding=encoding)
        for path in path.iterdir()
    }


def load_langs(path: str | Path, encoding: str | None = None) -> None:
    assert (path := Path(path)).is_dir()

    def gets(data: dict, key: str) -> Any:
        for subkey in key.split('.'):
            data = data[subkey]

        return data

    for path in path.iterdir():
        lang = load_lang(path, encoding=encoding)
        langs[path.name] = partial(gets, lang)


def _get(
    key: str,
    lang: str | Lang | None = None,
    depth: int = 0
) -> tuple[str, Lang]:
    if key.startswith('.'):
        key = modulename(depth + 1) + key

    if lang is None:
        lang = config['get_lang'](depth + 1)

    if isinstance(lang, str):
        lang = langs[lang]

    return key, lang


def raw(key: str, lang: str | Lang | None = None) -> Any:
    key, lang = _get(key, lang, depth=1)
    return lang(key)


def text(
    __key: str,
    __lang: str | None = None,
    /,
    **kwargs: Any
) -> str:
    key, lang = _get(__key, __lang, depth=1)
    data = lang(key)

    if isinstance(data, dict) and '' in data.keys():
        data = data['']

    assert isinstance(data, str)

    return parse(data.strip(), lang, kwargs)


def parse(text: str, lang: Lang, kwargs: dict[str, Any]) -> str:
    # comment
    text = re.sub(r'{{#.*?#}}', '', text, flags=re.DOTALL)

    # `text()` shortcut
    text = re.sub(
        r'{{%(.*?)%}}',
        lambda match: "{{text(f'''" + match[1].strip() + "''')}}",
        text,
        flags=re.DOTALL,
    )

    # list comprehension
    text = re.sub(
        r'{{\$(.*?)\$}}',
        lambda match: "{{'\\n'.join([" + match[1] + "])}}",
        text,
        flags=re.DOTALL,
    )

    # embedded Python code
    def repl(match: re.Match[str]) -> str:
        try:
            return str(eval(match[1].strip(), {
                'lang': lang,
                'raw': raw,
                'text': text,
                **kwargs
            }))
        except Exception:
            return config['on_exception']()
    text = re.sub(r'{{(.*?)}}', repl, text, flags=re.DOTALL)

    return text.replace(r'\{', '{').replace(r'\}', '}')
