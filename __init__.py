from flask import Flask
import os
import requests_cache
from requests_cache.backends.redis import RedisCache
class MyApp(Flask):
    def __init__(self):
        Flask.__init__(self,__name__)

app = MyApp()
app.config.from_envvar('CONFIG')
# client-side request caching (so caching the patreon api responses)
if app.config['REQUEST_CACHE_BACKEND'] == 'redis':
    backend = RedisCache(host=os.environ.get('REDIS_HOST'),
    port=os.environ.get('REDIS_PORT'))
    requests_cache.install_cache('github_cache',backend=backend,expire_after=app.config['REQUEST_CACHE_TIMEOUT'])
else:
    requests_cache.install_cache('github_cache',backend=app.config['REQUEST_CACHE_BACKEND'],expire_after=app.config['REQUEST_CACHE_TIMEOUT'])