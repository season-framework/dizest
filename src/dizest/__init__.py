from dizest import util
from .workflow import Workflow
from .server import Server

from .version import VERSION_STRING

cache = util.std.stdClass()
cache.server = util.std.stdClass()

def server(name, **kwargs):
    if name in cache.server:
        return cache.server[name]
    instance = Server(**kwargs)
    cache.server[name] = instance
    return instance

def instances():
    return [name for name in cache.server]

version = VERSION = __version__ = __VERSION__= VERSION_STRING