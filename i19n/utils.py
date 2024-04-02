from inspect import currentframe
from types import FrameType


def _getframe(depth: int = 0) -> FrameType:
    assert (frame := currentframe()) is not None

    for _ in range(depth + 1):
        assert (frame := frame.f_back) is not None

    return frame


def modulename(depth: int = 0) -> str:
    return _getframe(depth + 1).f_globals['__name__']
