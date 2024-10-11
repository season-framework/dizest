import os
import sys
import requests
import datetime
import season
import json
import uuid

Workflow = wiz.model("portal/dizest/struct/workflow")

class Model:
    def __init__(self, core, id=None, cwd=None, executable=None):
        self.core = core
        self.id = id
        if id is None:
            return
        
        self.path = None
        self.executable = None
        opts = core.config.spawner_option()
        opts['id'] = self.id
        if executable is not None:
            opts['executable'] = executable
            self.executable = executable

        if cwd is not None:
            opts['cwd'] = os.path.join(opts['cwd'], cwd)
        self.spawner = core.config.spawner_class(**opts)
        self.spawner.start()
        self.workflow = Workflow(self)
        self.timestamp = datetime.datetime.now()

    """
    static functions
    """
    def __call__(self, id, cwd=None, executable=None):
        cache = self.cache()
        print(self.core.config.kernel_id)

        def gen_kernel_id():
            if self.core.config.kernel_id is not None:
                return self.core.config.kernel_id()
            return str(uuid.uuid1())
        
        if id is None:
            id = gen_kernel_id()

        if id not in cache:
            id = gen_kernel_id()
            cache[id] = Model(self.core, id, cwd, executable)
        return cache[id]
    
    def get(self, id):
        cache = self.cache()
        if id not in cache:
            return None
        return cache[id]

    def cache(self):
        cache = self.core.cache()
        if 'kernel' not in cache:
            cache.kernel = season.util.stdClass()
        return cache.kernel
    
    def list(self):
        cache = self.core.cache().kernel
        res = []
        if cache is not None:
            for kernel_id in cache:
                kernel = cache[kernel_id]
                res.append(kernel)
        return res
        
    """
    instance functions
    """
    def stop(self):
        if self.id is None: return
        self.spawner.stop()
        cache = self.cache()
        if self.id in cache:
            del cache[self.id]

    def uri(self):
        if self.id is None: return
        return self.spawner.uri()

    def status(self):
        if self.id is None: return
        return self.spawner.status()
    
    def update(self, data):
        if self.path is None:
            return None
        path = self.path
        return self.workflow.update(path, data)
