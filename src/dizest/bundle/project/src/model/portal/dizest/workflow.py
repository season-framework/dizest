import requests
import datetime
import season
import dizest
import json

config = wiz.model("portal/dizest/config")

class Flow:
    def __init__(self, workflow):
        self.workflow = workflow

    def run(self, flow_id):
        return self.workflow.query(path=f"/flow/run/<namespace>/{flow_id}")
    
    def stop(self, flow_id):
        return self.workflow.query(path=f"/flow/stop/<namespace>/{flow_id}")
    
    def status(self):
        res = self.workflow.query(path="/workflow/flow_status/<namespace>")
        if res.code == 200:
            return res.data
        return dict()

class Model:
    def __init__(self, kernel, data, spec="base"):
        self.spawner = None
        self.kernel = kernel
        self.cache = dict()
        self.cache['data'] = data
        self.cache['spec'] = spec

        zone = self.kernel.zone
        workflow_id = self.id()

        self.flow = Flow(self)

    def spawner_id(self):
        return self.cache['data']['spawner_id']

    def data(self):
        return self.cache['data']

    def id(self):
        return self.cache['data']['id']

    def spec(self):
        spec = self.cache['spec']
        spec = self.kernel.spec(spec)
        return spec

    def set(self, **kwargs):
        for key in kwargs:
            self.cache[key] = kwargs[key]
        if self.spawner is None: return
        self.spawner.set(**kwargs)

    # API
    def query(self, method='get', path='', data=dict()):
        if self.spawner is None: return
        try:
            uri = self.spawner.uri()
            namespace = self.spawner_id()
            url = f"{uri}{path}".replace("<namespace>", namespace)
            if method == 'get':
                res = requests.get(url)
            else:
                res = requests.post(url, data=dict(namespace=namespace, **data))
            res = json.loads(res.text)
            res = season.util.std.stdClass(res)
        except Exception as e:
            res = season.util.std.stdClass(code=500, data=e)
        return res

    def start(self):
        if self.spawner is None:
            zone = self.kernel.zone
            spec = self.spec()
            workflow_id = self.id()
            if 'user' in self.cache:
                user = self.cache['user']
            else:
                user = config.user_id(wiz, zone)
            cwd = config.cwd(wiz, zone, workflow_id)
            socket_uri = config.socket_uri(wiz, zone, workflow_id)
            self.spawner = dizest.spawner.simple.SimpleSpawner(spec=spec, user=user, cwd=cwd, socket=socket_uri)

        if self.spawner.status() == 'stop':
            self.spawner.start()
        
        res = self.query(path="/workflow/status/<namespace>")
        if res.code != 200:
            package = self.data()
            package = json.dumps(package, default=season.util.string.json_default)
            res = self.query(method='post', path="/workflow/init", data=dict(package=package))        

    def kill(self):
        if self.spawner is None: return
        self.spawner.stop()
        self.spawner = None

    def restart(self):
        self.stop()
        self.start()
    
    def stop(self):
        if self.spawner is None: return
        self.query(path="/workflow/stop/<namespace>")
    
    def status(self):
        if self.spawner is None: 
            return 'stop'

        status = self.spawner.status()
        if status == 'stop':
            return 'stop'
        res = self.query(path="/workflow/status/<namespace>")
        if res.code == 200:
            return res.status
        return 'stop'
        
    def update(self, data=None):
        if data is None: data = self.data()
        
        zone = self.kernel.zone
        workflow_id = self.id()

        if data['id'] != workflow_id:
            return False

        self.cache['data'] = data
        config.update_workflow(wiz, zone, workflow_id, data)

        if self.spawner is not None:
            package = json.dumps(data, default=season.util.string.json_default)
            res = self.query(path="/workflow/status/<namespace>")
            if res.code != 200: self.query(method='post', path="/workflow/init", data=dict(package=package))
            else: self.query(method='post', path="/workflow/update", data=dict(package=package))

        return True

    def update_id(self, id):
        if self.id() != id:
            self.cache['data']['id'] = id
            zone = self.kernel.zone
            workflow_id = self.id()
            cwd = config.cwd(wiz, zone, workflow_id)

            if self.spawner is not None:
                self.spawner.set(cwd=cwd)
                self.restart()

    def run(self):
        if self.spawner is None: return
        return self.query(path="/workflow/run/<namespace>")

    def scheduler(self, jobs):
        if self.spawner is None: return
        jobs = json.dumps(jobs, default=season.util.string.json_default)
        return self.query(path="/workflow/scheduler/<namespace>", data=dict(jobs=jobs))
