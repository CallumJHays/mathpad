from typing import Optional, NamedTuple


class _GlobalOptions(NamedTuple):
    auto_simplify: bool = True


_global_options = _GlobalOptions()


def set_global_options(auto_simplify: Optional[bool] = None):
    if auto_simplify is not None:
        _global_options.auto_simplify = auto_simplify
