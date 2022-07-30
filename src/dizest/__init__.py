from dizest import util
from dizest import kernel
from .workflow import Workflow
from .version import VERSION_STRING, VERSIONS

cache = util.std.stdClass()
cache.manager = util.std.stdClass()

def load(name, **kwargs):
    if name in cache.manager:
        return cache.manager[name]
    instance = kernel.Manager(**kwargs)
    cache.manager[name] = instance
    return instance

def instances():
    return [name for name in cache.manager]

version = VERSION = __version__ = __VERSION__= VERSION_STRING
versions = VERSIONS