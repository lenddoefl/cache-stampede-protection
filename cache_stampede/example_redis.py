# coding: utf-8
"""
Example using python-redis-lock to prevent cache stampedes across
disparate processes/servers.
"""

from __future__ import absolute_import, division, print_function, \
  unicode_literals

from distutils.version import LooseVersion
from os import getpid
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


# Set up python-redis-lock client.
# Note: unlike the ``threading.Lock`` example,
# we don't initialize a global lock!
import redis_lock
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
    with redis_lock.Lock(redis_client, name=cache_key + '_lock'):


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
  # Note that we don't use threads in this case.
  # Instead we will background several processes using a loop in the
  # shell.  See the README file for more info.
  maybe_cache('some_other_key', expensive_computation)
