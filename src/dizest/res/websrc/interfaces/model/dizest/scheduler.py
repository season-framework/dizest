import season
import os
import sys
import datetime
import time
import urllib
sys.path.insert(0, '/opt/workspace/dizest/src')
import dizest

class Model:
    def __init__(self, wpid, package=None, develop=False):
        host = urllib.parse.urlparse(wiz.flask.request.base_url)
        host = f"{host.scheme}://{host.netloc}/dizest/api/kernel"
        session = wiz.model("session").use()
        
        # development not use cache
        if develop:
            cache = self.cache = wiz.model("dizest/cache").use("dizest.apps.cache")
            kernel = cache.get(wpid)
            if kernel is None:
                if package is not None:
                    cwd = os.path.realpath(season.core.PATH.PROJECT + "/../storage/local/" + session.get("id"))
                    workflow = dizest.Workflow(package, api=host, cwd=cwd, isdev=True, cache="/dev/shm/dizest")
                    workflow.user_id = session.get("id")
                    workflow.created = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    kernel = workflow.kernel()
                    cache.set(workflow.id(), kernel)
                else:
                    kernel = None

        # workflow use cache
        else:
            cache = self.cache = wiz.model("dizest/cache").use("dizest.workflow.cache")
            kernel = cache.get(wpid)
            if kernel is None:
                if package is not None:
                    cwd = os.path.realpath(season.core.PATH.PROJECT + "/../storage/local/" + session.get("id"))
                    workflow = dizest.Workflow(package, api=host, cwd=cwd, cache="/dev/shm/dizest")
                    workflow.user_id = session.get("id")
                    workflow.created = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    workflow.instance_id = int(time.time())
                    kernel = workflow.kernel()
                    cache.set(workflow.id(), kernel)
                else:
                    kernel = None

        self.kernel = kernel

        if package is not None:
            self.kernel.workflow.update(package)
            self.kernel.update()

    @staticmethod
    def dizest():
        return dizest

    @staticmethod
    def running():
        cache = wiz.model("dizest/cache").use("dizest.workflow.cache")
        return cache.keys()

    @staticmethod
    def test(fid):
        cache = wiz.model("dizest/cache").use("dizest.apps.cache")
        db = wiz.model("dizest/db").use("app")
        app = db.get(id=fid)

        workflow = dict()
        workflow['id'] = 'develop-' + fid
        
        workflow['flow'] = dict()
        flow = dict()
        flow['id'] = fid
        flow['app_id'] = fid
        flow['class'] = fid
        flow['inputs'] = dict()
        for i in range(len(app['inputs'])):
            obj = app['inputs'][i]
            if obj['type'] == 'output':
                flow['inputs'][obj['name']] = dict()
                flow['inputs'][obj['name']]['connections'] = list()
        flow['name'] = app['title']
        flow['order'] = 1
        flow['outputs'] = dict()
        for i in range(len(app['outputs'])):
            obj = app['outputs'][i]
            flow['outputs'][obj['name']] = dict()
            flow['outputs'][obj['name']]['connections'] = list()
        flow['pos_x'] = 0
        flow['pos_y'] = 0
        flow['data'] = dict()
        flow['typenode'] = False
        workflow['flow'][fid] = flow
        
        workflow['apps'] = dict()
        workflow['apps'][fid] = app

        return Model('develop-' + fid, workflow, develop=True)

    def instance_id(self):
        return self.kernel.workflow.instance_id

    def start(self):
        self.kernel.start()

    def restart(self):
        try:
            self.kernel.kill()
        except:
            pass
        try:
            self.kernel.start()
        except:
            pass

    def stop(self):
        if self.kernel is None:
            return
        self.kernel.stop()
    
    def kill(self):
        cache = self.cache
        if self.kernel is None:
            return
        self.kernel.kill()
        cache.delete(self.kernel.workflow.id())

    def run(self, flow_id):
        try:
            self.kernel.run(flow_id)
        except:
            self.start()
            self.kernel.run(flow_id)

    def update(self, package):
        self.kernel.workflow.update(package)
        self.kernel.update()

    def status(self, flow_id=None):
        res = season.stdClass()
        if self.kernel is None:
            return res
        
        flow = self.kernel.workflow.flow(flow_id)
        if flow is None: return res
        res.flow_id = flow.id()
        res.status = flow.status.get("status", "ready")
        res.index = flow.status.get("index", 1)
        res.code = flow.status.get("code", 0)
        res.message = flow.status.get("message", "")
        return res

    def flow(self, flow_id):
        return self.kernel.workflow.flow(flow_id)