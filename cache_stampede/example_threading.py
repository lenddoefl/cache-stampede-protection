# coding: utf-8
"""
Example using :py:class:`threading.Lock` to prevent cache stampedes
across multiple threads within a single process.
"""

from __future__ import absolute_import, division, print_function, \
  unicode_literals

import threading
from distutils.version import LooseVersion
from threading import Thread, current_thread
from time import sleep

from django import get_version
from django.core.cache import DEFAULT_CACHE_ALIAS

django_version = LooseVersion(get_version())
if django_version.version[0:2] < [1, 7]:
  # Django 1.6 and earlier
  # noinspection PyUnresolvedReferences
  from django.core.cache import get_cache
  cache = get_cache(DEFAULT_CACHE_ALIAS)
else:
  # Django 1.7 and later
  from django.core.cache import caches
  cache = caches[DEFAULT_CACHE_ALIAS]


def expensive_computation():
  """
  This is a routine that is very expensive (e.g., in terms of CPU utilization,
  3rd-party webservice usage, etc.), so we want to store the value in the
  cache whenever possible.
  """
  print(current_thread().name, ': Starting expensive computation')
  # Simulate expensive computation.
  sleep(5)
  result = 42
  print(current_thread().name, ': Finished expensive computation, result is', result)
  return result


# Create a single lock for the cache.
# We'll investigate more scalable approaches in the next section.
cache_lock = threading.Lock()

def maybe_cache(cache_key, func):
  """
  Checks the cache for the specified value.
  In the event of a cache miss, run the specified function and cache the result.
  """
  # Step 1: Check the cache.
  result = cache.get(cache_key)

  if result is None:
    # Step 2: Acquire lock.
    # If another thread owns the lock, this will block until the lock is released.
    print(current_thread().name, ': Waiting for lock')
    with cache_lock:
      print(current_thread().name, ': Acquired lock')
      # Step 3: Check the cache again.
      result = cache.get(cache_key)

      if result is None:
        # Step 4: Still not cached; run expensive computation.
        result = func()
        cache.set(cache_key, result)
      else:
        print(current_thread().name, ': Got result', result, 'from cache')

      # Step 5: Release the lock.
      # Note that this happens automatically
      # because we used the ``with`` keyword to acquire the lock.
      print(current_thread().name, ': Releasing lock')
  else:
    print(current_thread().name, ': Got result', result, 'from cache')

  return result


if __name__ == '__main__':
  # Initialize some threads for our cache stampede.
  def steer():
    maybe_cache('some_key', expensive_computation)

  threads = [Thread(target=steer) for _ in range(5)]

  for t in threads:
    t.start()

  for t in threads:
    t.join()
