import asyncio
from functools import wraps
from time import time

def guard_class_property(prop_name: str):
    def guard_decorator(fn):
        @wraps(fn)
        def guarded_fn(self, *args, **kwargs):
            if (hasattr(self, prop_name)):
                return fn(self, *args, **kwargs)

        return guarded_fn

    return guard_decorator


def accepts_cancelation(fn):
    @wraps(fn)
    def guarded_fn(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except asyncio.CancelledError:
            raise

    return guarded_fn


def measure_time(fn):
    @wraps(fn)
    def measured_fn(*args, **kwargs):
        start = time()
        res = fn(*args, **kwargs)
        duration = time() - start 

        print(f"Execution took {duration}")

        return res

    return measured_fn