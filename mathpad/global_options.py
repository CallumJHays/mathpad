from typing import Optional


class _GlobalOptions:
    auto_simplify: bool = True
    ipython_display_symbol_on_definition: bool = True
    ipython_display_eqn_on_definition: bool = False


_global_options = _GlobalOptions()

# TODO: make this a context manager


def set_global_options(auto_simplify: Optional[bool] = None):
    if auto_simplify is not None:
        _global_options.auto_simplify = auto_simplify
