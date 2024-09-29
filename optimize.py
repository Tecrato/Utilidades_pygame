from functools import wraps


def memosize(funcion):
    cache = {}
    @wraps(funcion)
    def wrapper(*args,**kwargs):
        key = str(args) + str(kwargs)

        if key not in cache:
            cache[key] = funcion(*args, **kwargs)

        return cache[key]
    return wrapper

