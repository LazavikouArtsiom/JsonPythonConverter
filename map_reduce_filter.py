def _map(func, *iterable):
    # for el in zip(*iterable):
    #     yield func(x)
    return (func(el) for el in zip(*iterable))

def _filter(func, *iterable):
    # for el in iterable:
    #     if func(el):
    #         yield el
    return (el for el in zip(*iterable) if func(el))

def _reduce(func, iterable):
    iterable = iter(iterable)
    value = next(iterable)
    for element in iterable:
        value = func(value, element)
    return value
