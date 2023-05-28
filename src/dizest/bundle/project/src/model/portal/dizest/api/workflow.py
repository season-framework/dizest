import requests
import season
import json
import inspect

def fncall(fn, **kwargs):
    args = inspect.getfullargspec(fn).args
    if len(args) > 0:
        if args[0] == 'self':
            args = args[1:]

    for i in range(len(args)):
        key = args[i]
        if key in kwargs: 
            args[i] = kwargs[key]
        else:
            args[i] = None
    
    return fn(*args)

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
    def __init__(self, kernel):
        self.__NAMESPACE__ = None
        self.kernel = kernel
        self.flow = Flow(self)
    
    def __call__(self, namespace):
        workflow = Model(self.kernel)
        workflow.__NAMESPACE__ = namespace
        return workflow

    def query(self, method='get', path='', data=dict()):
        try:
            uri = self.kernel.uri()
            namespace = self.namespace()
            url = f"{uri}/{path}".replace("<namespace>", namespace)
            if method == 'get':
                res = requests.get(url)
            else:
                res = requests.post(url, data=dict(namespace=namespace, **data))
            res = json.loads(res.text)
            res = season.util.std.stdClass(res)
        except Exception as e:
            res = season.util.std.stdClass(code=500, data=e)
        return res
    
    def get(self, workflow_id, **kwargs):
        config = wiz.model("portal/dizest/config")
        variables = dict()
        for key in kwargs:
            variables[key] = kwargs[key]
        variables['namespace'] = self.namespace()
        variables['workflow_id'] = workflow_id
        variables['kernel_id'] = self.kernel.kernel_id
        if 'acl' not in variables: variables['acl'] = True

        return fncall(config.get_workflow, **variables)

    def update(self, package, **kwargs):
        config = wiz.model("portal/dizest/config")
        workflow_id = package['id']

        variables = dict()
        for key in kwargs:
            variables[key] = kwargs[key]
        variables['namespace'] = self.namespace()
        variables['workflow_id'] = workflow_id
        variables['kernel_id'] = self.kernel.kernel_id
        variables['package'] = package
        variables['data'] = package
        if 'acl' not in variables: variables['acl'] = True

        fncall(config.update_workflow, **variables)

        package = json.dumps(package, default=season.util.string.json_default)
        res = self.query(path="/workflow/status/<namespace>")
        if res.code != 200:
            self.query(method='post', path="/workflow/init", data=dict(package=package))
        else:
            self.query(method='post', path="/workflow/update", data=dict(package=package))
        
    def run(self):
        return self.query(path="/workflow/run/<namespace>")

    def scheduler(self, jobs):
        jobs = json.dumps(jobs, default=season.util.string.json_default)
        return self.query(path="/workflow/scheduler/<namespace>", data=dict(jobs=jobs))
    
    def stop(self):
        return self.query(path="/workflow/stop/<namespace>")

    def status(self):
        if self.namespace() is None:
            try:
                uri = self.kernel.uri()
                res = requests.get(f"{uri}/workflow/status")
                res = json.loads(res.text)
                res = res['data']
                status = dict()
                for key in res:
                    if res[key]['index'] == 0:
                        status[key] = 'init'
                    else:
                        status[key] = res[key]['status']
                return status
            except:
                return dict()
        else:
            res = self.query(path="/workflow/status/<namespace>")
            if res.code == 200:
                return res.status
        return None

    def namespace(self):
        return self.__NAMESPACE__
