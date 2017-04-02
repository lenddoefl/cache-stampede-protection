# coding: utf-8
"""
Example using python-redis-lock to prevent cache stampedes across
disparate processes/servers.
"""

from __future__ import absolute_import, division, print_function, \
    unicode_literals

from os import getpid
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


# Set up python-redis-lock client.
# Note: unlike the ``threading.Lock`` example,
# we don't initialize a global lock!
from redis_lock import Lock
redis_client = cache.get_client(None)


def expensive_computation():
  print(getpid(), ': Starting expensive computation')
  sleep(5)
  result = 42
  print(getpid(), ': Finished expensive computation, result is', result)
  return result

def maybe_cache(cache_key, func):
  # Step 1: Check the cache.
  result = cache.get(cache_key)

  if result is None:
    # Step 2: Acquire lock.
    print(getpid(), ': Waiting for lock')


    # Note that we create a new Lock instance each time.
    # The lock name is used to synchronize access between processes.
    with Lock(redis_client, name=cache_key + '_lock'):


      print(getpid(), ': Acquired lock')
      # Step 3: Check the cache again.
      result = cache.get(cache_key)

      if result is None:
        # Step 4: Still not cached; run expensive computation.
        result = func()
        cache.set(cache_key, result)
      else:
        print(getpid(), ': Got result', result, 'from cache')

      # Step 5: Release the lock.
      print(getpid(), ': Releasing lock')
  else:
    print(getpid(), ': Got result', result, 'from cache')

  return result

if __name__ == '__main__':
  maybe_cache('some_other_key', expensive_computation)
