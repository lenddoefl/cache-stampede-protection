# Preventing Cache Stampedes Using `python-redis-lock`
This is a companion repo for the blog post, "Preventing Cache Stampedes Using
python-redis-lock" on the EFL Technology Blog.

It contains two example scripts that show how to use locks to prevent "cache
stampedes" when cached values become stale:

- `cache_stampede/example_threading.py` proves the concept by using
  `threading.Lock` to control access to the cache among multiple threads in a
  single process.
- `cache_stampede/example_redis.py` takes it a step further by moving the lock
  into Redis itself, allowing access to be controlled across multiple processes,
  even multiple servers.

## Running the Examples
To run the example scripts:

Set up the Django project (only has to be done once):

1. [Create a virtualenv](https://virtualenvwrapper.readthedocs.io/en/latest/),
  if desired.
2. `pip install -r requirements.txt`
3. Ensure Redis is running, and configure `cache_stampede/settings.py:CACHES`
  if necessary (by default it is configured to connect to `localhost:6379`).
4. `cd` to the root directory of the project.

### `threading.Lock` Example:
```
> DJANGO_SETTINGS_MODULE="settings" python cache_stampede/example_therading.py
```

### `python-redis-lock` Example:
```
> for _ in {1..5}; do DJANGO_SETTINGS_MODULE="settings" python cache_stampede/example_redis.py & done
```
