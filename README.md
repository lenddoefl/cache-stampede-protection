# Preventing Cache Stampedes Using `python-redis-lock`
This is a companion repo for the blog post, ["Preventing Cache Stampedes Using
python-redis-lock"](https://www.eflglobal.com/preventing-cache-stampedes-with-python-redis-lock/)
on the EFL Technology Blog.

It contains three example scripts that show how to use locks to prevent "cache
stampedes" when cached values become stale:

- `cache_stampede/example_no_protection.py` shows what happens during a cache
  stampede.
- `cache_stampede/example_threading.py` proves the concept by using
  `threading.Lock` to control access to the cache among multiple threads in a
  single process.
- `cache_stampede/example_redis.py` takes it a step further by moving the lock
  into Redis itself, allowing access to be controlled across multiple processes,
  even multiple servers.

## Running the Examples
This project is compatible with Python 3.6 and 2.7.

Set up the Django project (only has to be done once):

1. [Create a virtualenv](https://virtualenvwrapper.readthedocs.io/en/latest/),
  if desired.
2. `pip install -r requirements.txt`
3. Ensure Redis is running, and configure `cache_stampede/settings.py:CACHES`
  if necessary (by default it is configured to connect to `localhost:6379`).
4. `cd` to the root directory of the project.

To run the example scripts, execute the following commands (tested in bash and
zsh):

### Cache Stampede Example:
This is the "control group", showing what happens during a cache stampede.
```bash
redis-cli -n 1 FLUSHDB
DJANGO_SETTINGS_MODULE="settings" python cache_stampede/example_no_protection.py
```

### `threading.Lock` Example:
This example uses `threading.Lock` to prevent a cache stampede.
```bash
redis-cli -n 1 FLUSHDB
DJANGO_SETTINGS_MODULE="settings" python cache_stampede/example_threading.py
```

### `python-redis-lock` Example:
This example uses `python-redis-lock` to prevent a cache stampede.
```bash
redis-cli -n 1 FLUSHDB
for _ in {1..5}; do DJANGO_SETTINGS_MODULE="settings" python cache_stampede/example_redis.py & done
```

You may see a single `UNLOCK_SCRIPT not cached.` warning in the output.

Releasing a lock requires several commands that must run atomically (this
requires a [LUA script](https://redis.io/commands/eval)).  For better
performance, `python-redis-lock` uses the
[EVALSHA](https://redis.io/commands/evalsha) command so that the LUA script gets
cached after the first time it is eval'd.

`UNLOCK_SCRIPT not cached.` simply means that the LUA script hasn't been cached
by Redis yet.  It is safe to ignore this warning, as long as it only appears
once.
