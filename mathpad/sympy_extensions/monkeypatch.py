
def monkeypatch_method(cls):
    "decorator to monkey-patch a method into a class"
    # https://mail.python.org/pipermail/python-dev/2008-January/076194.html
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func
    return decorator