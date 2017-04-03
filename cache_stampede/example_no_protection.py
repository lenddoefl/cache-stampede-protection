# coding: utf-8
"""
Example showing what happens when no measures are employed to prevent
cache stampedes.
"""

from __future__ import absolute_import, division, print_function, \
    unicode_literals

from threading import Thread, current_thread
from time import sleep

from django.core.cache import DEFAULT_CACHE_ALIAS

try:
  # Django 1.7 and later
  from django.core.cache import caches
  cache = caches[DEFAULT_CACHE_ALIAS]
except ImportError:
  # Django 1.6 and earlier
  from django.core.cache import get_cache
  cache = get_cache(DEFAULT_CACHE_ALIAS)

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

def maybe_cache(cache_key, func):
  """
  Checks the cache for the specified value.
  In the event of a cache miss, run the specified function and cache the result.
  """
  # Step 1: Check the cache.
  result = cache.get(cache_key)

  if result is None:
    # Step 2: Value is not cached; recompute and store the value.
    result = func()
    cache.set(cache_key, result)
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
