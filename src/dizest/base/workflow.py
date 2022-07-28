# import copy
import os
# import multiprocessing as mp
# import time
# import json
# import traceback
# import sys
# import requests
# import pypugjs
# import sass

from dizest import util
from dizest.core import kernel

class Options(util.std.stdClass):
    def __getattr__(self, attr):
        obj = self.get(attr)
        if type(obj) == dict:
            return stdClass(obj)
        if obj is None:
            if attr == 'api': return None
            if attr == 'cwd': return os.getcwd()
            if attr == 'cache': return os.path.join(os.getcwd(), ".dizest", "cache")
            if attr == 'isdev': return False
        return obj

class Workflow(util.std.stdClass):
    def __init__(self, package, **opts):
        self.package = package
        self.opts = Options(**opts)