import requests
import datetime
import season
import dizest
import json

Config = wiz.model("portal/dizest/config")
Drive = wiz.model("portal/dizest/api/drive")
Workflow = wiz.model("portal/dizest/api/workflow")

class Model:
    def __init__(self, kernel_id, spec=dict(name="base"), socket=None, user=None, cwd=None):
        self.kernel_id = kernel_id
        if user is None:
            session = wiz.model("portal/season/session")
            user = session.user_id()
        self.user = user
        self.cwd = cwd
        self.socket = socket

        # load spawner
        self.spanwer = dizest.spawner.simple.SimpleSpawner(spec=spec, user=user, cwd=cwd, socket=socket)
        self.drive = Drive(self)
        self.workflow = Workflow(self)

    @staticmethod
    def cache():
        if 'dizest' not in wiz.server.app: 
            wiz.server.app.dizest = season.util.std.stdClass()
        cache = wiz.server.app.dizest
        if 'kernel' not in cache:
            cache.kernel = season.util.std.stdClass()
        return cache.kernel

    @staticmethod
    def getInstance(kernel_id=None):
        if kernel_id is None: kernel_id = Config.kernel_id()
        cache = Model.cache()
        if kernel_id in cache:
            return cache[kernel_id]
        return None

    @staticmethod
    def createInstance(kernel_id=None, **kwargs):
        if kernel_id is None: kernel_id = Config.kernel_id()

        cache = Model.cache()
        if kernel_id in cache:
            return cache[kernel_id]
        cache[kernel_id] = Model(kernel_id, **kwargs)
        return cache[kernel_id]

    @staticmethod
    def isInstance(kernel_id=None):
        if kernel_id is None: kernel_id = Config.kernel_id()
        cache = Model.cache()
        if kernel_id in cache:
            return True
        return False

    @staticmethod
    def specs():
        fs = Config.fs()
        specs = fs.read.json("spec.json", [])
        if len(specs) == 0:
            specs.append(dict(name="base"))
        return specs

    def uri(self):
        return self.spanwer.uri()

    def start(self):
        self.spanwer.start()

    def restart(self):
        self.spanwer.stop()
        self.spanwer.start()

    def stop(self):
        self.spanwer.stop()
        cache = Model.cache()
        kernel_id = self.kernel_id
        if kernel_id in cache:
            del cache[kernel_id]

    def status(self):
        return self.spanwer.status()

    def set(self, **kwargs):
        self.spanwer.set(**kwargs)
