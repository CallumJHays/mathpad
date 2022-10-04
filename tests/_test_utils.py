
def _expect_assertion_error(f):
    try:
        f()
    except AssertionError:
        pass
    else:
        assert False, "Expected AssertionError"