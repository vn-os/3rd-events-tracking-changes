"""
Asynchronous Cached with asyncio library
Note: Append key with None value first before enter function then re-update value after leave function
"""
import functools
import inspect
from cachetools import keys

__all__ = ["cached"]

class nullcontext:
  """A class for noop context managers."""

  def __enter__(self):
    """Return ``self`` upon entering the runtime context."""
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    """Raise any exception triggered within the runtime context."""
    return None

  async def __aenter__(self):
    """Return ``self`` upon entering the runtime context."""
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    """Raise any exception triggered within the runtime context."""
    return None

def cached(cache, key=keys.hashkey, lock=None):
  """
  Decorator to wrap a function or a coroutine with a memoizing callable
  that saves results in a cache.

  When ``lock`` is provided for a standard function, it's expected to
  implement ``__enter__`` and ``__exit__`` that will be used to lock
  the cache when gets updated. If it wraps a coroutine, ``lock``
  must implement ``__aenter__`` and ``__aexit__``.
  """
  lock = lock or nullcontext()

  def decorator(func):
    if inspect.iscoroutinefunction(func):

      async def wrapper(*args, **kwargs):
        k = key(*args, **kwargs)
        try:
          async with lock:
            return cache[k]

        except KeyError:
          pass  # key not found

        try:
          async with lock:
            cache[k] = None
        except ValueError:
          pass

        val = await func(*args, **kwargs)

        try:
          async with lock:
            cache[k] = val
        except ValueError:
          pass

        return val

    else:

      def wrapper(*args, **kwargs):
        k = key(*args, **kwargs)
        try:
          with lock:
            return cache[k]

        except KeyError:
          pass # key not found

        try:
          with lock:
            cache[k] = None
        except ValueError:
          pass

        val = func(*args, **kwargs)

        try:
          with lock:
            cache[k] = val
        except ValueError:
          pass

        return val

    return functools.wraps(func)(wrapper)

  return decorator
