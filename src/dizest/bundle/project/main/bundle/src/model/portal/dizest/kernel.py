import os
import sys
import requests
import datetime
import season
import json
import string as _string
import random as _random

config = wiz.model("portal/dizest/config")
Workflow = wiz.model("portal/dizest/workflow")

class Model:
    def __init__(self, zone):
        self.zone = zone

    def cache(self):
        zone = self.zone
        if 'dizest' not in wiz.server.app: 
            wiz.server.app.dizest = season.util.stdClass()
        cache = wiz.server.app.dizest
        if zone not in cache:
            cache[zone] = season.util.stdClass()
        return cache[zone]
    
    def random(self, length=16, number=False):
        string_pool = _string.ascii_letters + _string.digits
        if number:
            string_pool = _string.digits
        result = ""
        for i in range(length):
            result += _random.choice(string_pool)
        return result.lower()

    def delete_workflow(self, spawner_id):
        cache = self.cache()
        if spawner_id in cache:
            workflow = cache[spawner_id]
            workflow.kill()
            del cache[spawner_id]

    def workflow_by_spawner(self, spawner_id):
        cache = self.cache()
        if spawner_id in cache:
            return cache[spawner_id]
        return None

    def workflow(self, workflow_id):
        zone = self.zone
        cache = self.cache()

        data = config.get_workflow(wiz, zone, workflow_id)
        data['id'] = workflow_id

        spawner_id = None
        if 'spawner_id' in data:
            spawner_id = data['spawner_id']
        if spawner_id in cache:
            cache[spawner_id].update_id(workflow_id)
            return cache[spawner_id]

        spawner_id = self.random(16)
        while spawner_id in cache:
            spawner_id = self.random(16)        
        data['spawner_id'] = spawner_id

        workflow = Workflow(self, data)
        cache[spawner_id] = workflow
        config.update_workflow(wiz, zone, workflow_id, data)
        
        return workflow
    
    def workflows(self):
        res = dict()
        cache = self.cache()
        for key in cache:
            if cache[key].status() != 'stop':
                res[cache[key].id()] = dict(spawner_id=key, status=cache[key].status())
        return res

    def spec(self, name):
        condapath = config.condapath
        condafs = season.util.fs(condapath)
        specs = self.specs()
        for spec in specs:
            if spec['conda'] == name:
                return spec
        return dict(name="base", title="base", conda="base", executable=condafs.abspath(sys.executable))

    @staticmethod
    def specs():
        def hasDizest(condafs, env):
            path = os.path.join("envs", env, "bin", "dizest")
            return condafs.exists(path)

        condapath = config.condapath
        condafs = season.util.fs(condapath)
        envs = condafs.list("envs")
        res = []

        env = "base"
        basepath = condafs.abspath(sys.executable)
        res.append(dict(name=env, title=env, conda=env, executable=basepath))

        for env in envs:
            if env[0] == ".": continue
            if condafs.isdir(os.path.join("envs", env)):
                path = os.path.join("envs", env, "bin", "python")
                path = condafs.abspath(path)
                
                if hasDizest(condafs, env) == False:
                    continue
                if path == basepath: 
                    continue
                res.append(dict(name=env, title=env, conda=env, executable=path))
        return res