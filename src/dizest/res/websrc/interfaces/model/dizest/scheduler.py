import season
import os
import sys
import datetime
import time
import dizest
import urllib

class Model:
    def __init__(self, wpid, package=None, develop=False, logger=None):
        host = urllib.parse.urlparse(wiz.flask.request.base_url)
        session = wiz.model("session").use()
        
        # development not use cache
        if develop:
            host = f"{host.scheme}://{host.netloc}/dizest/api/kernel/dev_status"
            cache = self.cache = wiz.model("dizest/cache").use("dizest.apps.cache")
            wp = cache.get(wpid)
            if wp is None:
                if package is not None:
                    BASEPATH = os.path.realpath(season.core.PATH.PROJECT + "/../storage")
                    wp = dizest.Workflow(package, status_changed_api=host, cwd=BASEPATH, user=session.get("id"), auth=session.get("role"), logger=logger, develop=develop)
                    wp.set_status("user_id", session.get("id"))
                    wp.set_status("craeted", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    wp.instance_id = int(time.time())
                    cache.set(wp.id(), wp)
                else:
                    wp = None

        # workflow use cache
        else:
            host = f"{host.scheme}://{host.netloc}/dizest/api/kernel/changed"
            cache = self.cache = wiz.model("dizest/cache").use("dizest.workflow.cache")
            wp = cache.get(wpid)
            if wp is None:
                if package is not None:
                    BASEPATH = os.path.realpath(season.core.PATH.PROJECT + "/../storage")
                    wp = dizest.Workflow(package, status_changed_api=host, cwd=BASEPATH, user=session.get("id"), auth=session.get("role"), logger=logger, develop=develop)
                    wp.set_status("user_id", session.get("id"))
                    wp.set_status("craeted", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    wp.instance_id = int(time.time())
                    cache.set(wp.id(), wp)
                else:
                    wp = None

        self.workflow = wp
        
        if package is not None:
            self.workflow.update(package)

    @staticmethod
    def running():
        cache = wiz.model("dizest/cache").use("dizest.workflow.cache")
        return cache.keys()

    @staticmethod
    def test(fid, logger=None):
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

        return Model('develop-' + fid, workflow, develop=True, logger=logger)

    def instance_id(self):
        return self.workflow.instance_id

    def start(self):
        self.workflow.start()

    def restart(self):
        self.workflow.restart()

    def stop(self, flow_id=None):
        cache = self.cache

        if self.workflow is None:
            return None

        self.workflow.stop(flow_id)
        
        if flow_id is None:
            cache.delete(self.workflow.id())
        else:
            current = self.workflow.flow(flow_id)
            res = season.stdClass()
            res.flow_id = current.id()
            res.status = current.get_status("status", "ready")
            res.index = current.get_status("index", 1)
            res.code = current.get_status("code", 0)
            res.message = current.get_status("message", "")
            return res
        return None

    def run(self, flow_id):
        try:
            self.workflow.run(flow_id)
        except:
            self.start()
            self.workflow.run(flow_id)

    def update(self, package):
        self.workflow.update(package)

    def status(self, flow_id=None):
        res = season.stdClass()
        if self.workflow is None:
            return res
        current = self.workflow.flow(flow_id)
        if current is None: 
            return res
        res.flow_id = current.id()
        res.status = current.get_status("status", "ready")
        res.index = current.get_status("index", 1)
        res.code = current.get_status("code", 0)
        res.message = current.get_status("message", "")
        return res

    def flow(self, flow_id):
        return self.workflow.flow(flow_id)