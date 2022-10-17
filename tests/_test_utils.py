
from typing import Type
from contextlib import contextmanager

@contextmanager
def expect_err(ExcType: Type[Exception]):
    try:
        yield
    except ExcType:
        pass
    else:
        assert False, f"Expected {ExcType.__name__} to be raised"
