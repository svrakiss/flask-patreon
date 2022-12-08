from flask import Flask
import requests_cache
class MyApp(Flask):
    def __init__(self):
        Flask.__init__(self,__name__)

app = MyApp()
app.config.from_envvar('CONFIG')
# client-side request caching (so caching the patreon api responses)
requests_cache.install_cache('github_cache',backend=app.config['REQUEST_CACHE_BACKEND'],expire_after=app.config['REQUEST_CACHE_TIMEOUT'])