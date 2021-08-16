
from typing import Callable, get_type_hints

# from eqns.mathpad import Equation


def relation(fn):
    # TODO: check input types and constraints
    def wrap(**kwargs):
        return fn(**kwargs)

    wrap.__name__ = fn.__name__
    wrap.__doc__ = f'{fn.__doc__}\n\n' + '\n'.join(
        f"{argname} [{ann.__metadata__[0]}]: {ann.__metadata__[1]}"
        for argname, ann
        in get_type_hints(fn, include_extras=True).items()
        if argname != 'return'
    )
    return wrap
