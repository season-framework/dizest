import requests
import datetime
import season
import json

class Flow:
    def __init__(self, workflow):
        self.workflow = workflow

    def run(self, flow_id):
        if self.workflow.data is None: return
        return self.workflow.query(path=f"/flow/run/{flow_id}")
    
    def stop(self, flow_id):
        if self.workflow.data is None: return
        return self.workflow.query(path=f"/flow/stop/{flow_id}")
    
    def status(self):
        if self.workflow.data is None: return
        res = self.workflow.query(path="/flow/status")
        if res.code == 200:
            return res.data
        return dict()

class Model:
    def __init__(self, kernel):
        self.kernel = kernel
        self.data = None
        self.flow = Flow(self)

    def query(self, method='get', path='', data=dict()):
        try:
            uri = self.kernel.uri()
            url = f"{uri}{path}"
            if method == 'get':
                res = requests.get(url)
            else:
                res = requests.post(url, data=data)
            res = json.loads(res.text)
            res = season.util.stdClass(res)
        except Exception as e:
            res = season.util.stdClass(code=501, data=e)
        return res
        
    def update(self, path, data=None):
        if data is None: data = self.data
        else: self.data = data

        if self.kernel is not None:
            self.data['kernel_id'] = self.kernel.id
            self.kernel.core.config.update_workflow(path, self.data)
            package = json.dumps(self.data, default=season.util.string.json_default)
            self.query(method='post', path="/workflow/update", data=dict(package=package))

        return self.data

    def status(self):
        if self.kernel is None: return
        if self.data is None: return
        
        if self.kernel is None: 
            return 'stop'

        status = self.kernel.status()
        if status == 'stop':
            return 'stop'
        res = self.query(path="/workflow/status")
        if res.code == 200:
            return res.status
        return 'stop'
    
    def run(self):
        if self.kernel is None: return
        if self.data is None: return
        return self.query(path="/workflow/run")

    def stop(self):
        if self.kernel is None: return
        if self.data is None: return
        self.query(path="/workflow/stop")
    
