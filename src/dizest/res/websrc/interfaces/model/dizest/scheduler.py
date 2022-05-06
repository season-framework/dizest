import season
import os
import sys
import datetime
sys.path.insert(0, '/opt/workspace/dizest/src')
import dizest
import urllib

cache = wiz.model("dizest/cache").use("dizest.workflow.cache")

class Model:
    def __init__(self, wpid, package=None):
        host = urllib.parse.urlparse(wiz.flask.request.base_url)
        host = f"{host.scheme}://{host.netloc}/dizest/api/kernel/changed"

        wp = cache.get(wpid)
        if wp is None:
            if package is not None:
                wp = dizest.Workflow(package, status_changed_api=host)
                session = wiz.model("session").use()
                wp.set_status("user_id", session.get("id"))
                wp.set_status("craeted", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                cache.set(wp.id(), wp)
            else:
                wp = None
        self.workflow = wp
        
        if package is not None:
            self.workflow.update(package)

    @staticmethod
    def running():
        return cache.keys()

    def start(self):
        self.workflow.start()

    def restart(self):
        self.workflow.restart()

    def stop(self, flow_id=None):
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