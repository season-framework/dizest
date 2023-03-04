import requests
import datetime
import season
import dizest
import json

class Flow:
    def __init__(self, workflow):
        self.workflow = workflow

    def run(self, flow_id):
        self.workflow.query(path=f"/flow/run/<channel>/{flow_id}")
    
    def stop(self, flow_id):
        self.workflow.query(path=f"/flow/stop/<channel>/{flow_id}")
    
class Workflow:
    def __init__(self, uweb, zone, workflow_id):
        self.uweb = uweb
        self.zone = zone
        self.id = workflow_id
        self.flow = Flow(self)
                
    def query(self, method='get', path='', data=dict()):
        try:
            uri = self.uweb.uri()
            channel = self.channel()
            url = f"{uri}/{path}".replace("<channel>", channel)
            if method == 'get':
                res = requests.get(url)
            else:
                res = requests.post(url, data=dict(channel=channel, **data))
            res = json.loads(res.text)
            res = season.util.std.stdClass(res)
        except Exception as e:
            res = season.util.std.stdClass(code=500, data=e)
        return res
    
    def update(self, package):
        package = json.dumps(package, default=season.util.string.json_default)
        res = self.query(path="/workflow/status/<channel>")
        if res.code != 200:
            self.query(method='post', path="/workflow/init", data=dict(package=package))
        else:
            self.query(method='post', path="/workflow/update", data=dict(package=package))
        
    def run(self):
        return self.query(path="/workflow/run/<channel>")

    def scheduler(self, jobs):
        jobs = json.dumps(jobs, default=season.util.string.json_default)
        return self.query(path="/workflow/scheduler/<channel>", data=dict(jobs=jobs))
    
    def stop(self):
        return self.query(path="/workflow/stop/<channel>")

    def status(self):
        res = self.query(path="/workflow/status/<channel>")
        if res.code == 200:
            return res.status
        return None
    
    def flow_status(self):
        res = self.query(path="/workflow/flow_status/<channel>")
        if res.code == 200:
            return res.data
        return dict()

    def channel(self):
        zone = self.zone
        workflow_id = self.id
        channel = self.uweb.dconfig.channel(zone=zone, workflow_id=workflow_id)
        return channel

class Drive:
    def __init__(self, uweb):
        self.uweb = uweb

    def __request__(self, fnname, **kwargs):
        kwargs["url"] = self.uweb.uri() + "/drive/" + fnname
        kwargs["allow_redirects"] = False
        return requests.request(**kwargs)

    def ls(self, path):
        if len(path) > 0:
            if path[0] == "/": 
                path = path[1:]
        return self.__request__(f"ls/{path}", method="GET", timeout=3)

    def create(self, path, data):
        if len(path) > 0:
            if path[0] == "/": 
                path = path[1:]
        return self.__request__(f"create/{path}", method="POST", data=data, timeout=3)

    def rename(self, path, data):
        if len(path) > 0:
            if path[0] == "/": 
                path = path[1:]
        return self.__request__(f"rename/{path}", method="POST", data=data, timeout=3)

    def remove(self, path, data):
        if len(path) > 0:
            if path[0] == "/": 
                path = path[1:]
        return self.__request__(f"remove/{path}", method="POST", data=data, timeout=3)
    
    def upload(self, path, **kwargs):
        if len(path) > 0:
            if path[0] == "/": 
                path = path[1:]
        return self.__request__(f"upload/{path}", **kwargs)

    def download(self, path):
        if len(path) > 0:
            if path[0] == "/": 
                path = path[1:]
        return self.__request__(f"download/{path}", method="GET")

class Model:
    def __init__(self, kernelspec=dict(name="base")):
        # global cache setting
        if 'dizest' not in wiz.server.app:
            wiz.server.app.dizest = season.util.std.stdClass()
        cache = wiz.server.app.dizest
        if 'dizest' not in cache:
            cache.dizest = season.util.std.stdClass()

        # config load
        dconfig = wiz.model("portal/dizest/dconfig")
        self.dconfig = dconfig

        
        dsocket_api = dconfig.dsocket()
        user = dconfig.user()
        kernel_user = dconfig.kernel_user()
        cwd = dconfig.cwd()

        # create spawner
        if user not in cache.dizest:
            spanwer = dizest.spawner.simple.SimpleSpawner(kernelspec=kernelspec, user=kernel_user, cwd=cwd, dSocket=dsocket_api)
            cache.dizest[user] = spanwer
        else:
            spanwer = cache.dizest[user]

        self.spanwer = spanwer
        self.drive = Drive(self)

    @staticmethod
    def getInstance(user):
        cache = wiz.server.app.dizest
        if 'dizest' in cache:
            if user in cache.dizest:
                return cache.dizest[user]
        return None

    def uri(self):
        return self.spanwer.uri()

    def start(self):
        self.spanwer.start()

    def restart(self):
        self.spanwer.stop()
        self.spanwer.start()

    def stop(self):
        self.spanwer.stop()
    
    def clear(self):
        try:
            self.stop()
        except:
            pass
        cache = wiz.server.app.dizest
        if 'dizest' in cache:
            user = self.dconfig.user()
            if user in cache.dizest:
                del cache.dizest[user]

    def status(self):
        return self.spanwer.status()

    def kernel(self, kernelspec=None):
        if kernelspec is not None:
            self.spanwer.setMeta(kernelspec=kernelspec)
        return self.spanwer.getMeta("kernelspec")

    def workflow(self, zone="dizest", workflow_id=None):
        return Workflow(self, zone, workflow_id) 
    
    def workflow_status(self):
        try:
            uri = self.uri()
            res = requests.get(f"{uri}/workflow/status")
            res = json.loads(res.text)
            res = res['data']
            status = dict()
            for key in res:
                status[res[key]['id']] = res[key]['status']
            return status
        except:
            return dict()