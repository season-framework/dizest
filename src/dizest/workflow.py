from dizest import util
import requests
import pypugjs
import sass

class App:
    def __init__(self, workflow, package):
        self.package = package
        self.workflow = workflow

    def id(self):
        return self.package['id']

    def get(self, key, default=None):
        try:
            return self.package[key]
        except Exception as e:
            pass
        return default

    def code(self):
        return self.package['code']

    def api(self):
        return self.package['api']

    def outputs(self):
        return [x['name'] for x in self.package['outputs']]

    def inputs(self):
        return self.package['inputs']

class Flow:
    def __init__(self, workflow, package):
        self.package = package
        self.workflow = workflow

    def id(self):
        return self.package['id']

    def active(self):
        if 'inactive' not in self.package:
            return True
        if self.package['inactive']:
            return False
        return True

    def app(self):
        app_id = self.package['app_id']
        return self.workflow.app(app_id)

    def data(self):
        flow = self.package
        
        app = self.app()
        code = app.code()
        outputs = app.outputs()
        
        appinput = app.inputs()
        inputs = dict()
        for val in appinput:
            vtype = val['type']
            vname = val['name']
            if vtype == 'output':
                cons = [[x['node'], x['input']] for x in flow['inputs'][vname]['connections']]
                inputs[vname] = {"type": vtype, "data": cons}
            elif vtype == 'variable':
                if vname in flow['data']:
                    inputs[vname] = ({"type": vtype, "data": flow['data'][vname]})
        
        return flow['id'], code, inputs, outputs

    def status(self):
        if self.workflow.spawner is None:
            return 'ready'
        flow = self.workflow.spawner.flow(self.id())
        return flow.status

    def index(self):
        if self.workflow.spawner is None:
            return ''
        flow = self.workflow.spawner.flow(self.id())
        return flow.index

    def log(self):
        if self.workflow.spawner is None:
            return ''
        flow = self.workflow.spawner.flow(self.id())
        return flow.log[:]

    def run(self):
        if self.workflow.spawner is None:
            raise Exception("Spawner is not connected")
        if self.status() == 'running':
            raise Exception("already running")
        self.workflow.spawner.run(self.id())
        return True

    def api(self, fnname, **kwargs):
        if self.workflow.spawner is None:
            raise Exception("Spawner is not connected")
        kwargs["url"] = self.workflow.spawner.uri + "/api/" + self.id() + "/" + fnname
        kwargs["allow_redirects"] = False
        return requests.request(**kwargs)

    def render(self, **kwargs):
        app = self.app()
        pugconfig = dict()
        pugconfig['variable_start_string'] = '{$'
        pugconfig['variable_end_string'] = '$}'

        pug = app.get("pug", "")
        pug = pypugjs.Parser(pug)
        pug = pug.parse()
        pug = pypugjs.ext.jinja.Compiler(pug, **pugconfig).compile()

        head = app.get("head", "")
        head = pypugjs.Parser(head)
        head = head.parse()
        head = pypugjs.ext.jinja.Compiler(head, **pugconfig).compile()

        js = app.get("js")
        if js is None or len(js) == 0:
            js = ""
        else:
            js = f"<script type='text/javascript'>{js}</script>"

        css = app.get("css")
        try:
            css = sass.compile(string=css)
            css = str(css)
            css = f"<style>{css}</style>"
        except:
            css = ""

        _head = ""
        _body = ""
        if 'head' in kwargs: _head = kwargs['head']
        if 'body' in kwargs: _body = kwargs['body']

        view = f"<!DOCTYPE html><html><head>{head}{_head}{css}</head><body>{pug}{_body}{js}</body></html>"
        return view

class DriveAPI:
    def __init__(self, workflow):
        self.workflow = workflow

    def __request__(self, fnname, **kwargs):
        if self.workflow.spawner is None:
            raise Exception("Spawner is not connected")
        kwargs["url"] = self.workflow.spawner.uri + "/drive/" + fnname
        kwargs["allow_redirects"] = False
        return requests.request(**kwargs)

    def ls(self, path):
        if len(path) > 0:
            if path[0] == "/": 
                path = path[1:]
        return self.__request__(f"ls/{path}", method="GET")

    def rename(self, path, data):
        if len(path) > 0:
            if path[0] == "/": 
                path = path[1:]
        return self.__request__(f"rename/{path}", method="POST", data=data)

    def remove(self, path, data):
        if len(path) > 0:
            if path[0] == "/": 
                path = path[1:]
        return self.__request__(f"remove/{path}", method="POST", data=data)
    
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

class Workflow:
    def __init__(self, package):
        required = ['id', 'apps', 'flow']
        for req in required:
            if req not in package:
                raise Exception(f"`{req}` not defined")
        self.package = package
        self.spawner = None
        self.manager = None
        self.kernel_name = None
        self.cwd = None
        self.drive_api = DriveAPI(self)

    def id(self):
        return self.package['id']

    def flows(self):
        flows = []
        for flow_id in self.package['flow']:
            flows.append(self.package['flow'][flow_id])
        flows.sort(key=lambda x: x['order'])
        return [x['id'] for x in flows]

    def app(self, app_id):
        if app_id not in self.package['apps']:
            return None
        app = self.package['apps'][app_id]
        return App(self, app)

    def flow(self, flow_id):
        if flow_id not in self.package['flow']:
            return None
        flow = self.package['flow'][flow_id]
        return Flow(self, flow)

    def kernelspec(self):
        if self.spawner is None: return None
        return self.spawner.kernel

    def storage(self):
        if self.spawner is None: return None
        return self.spawner.storage()

    def update(self, package):
        self.package = package
        if self.spawner is not None:
            self.spawner.update()

    # spawn kernel
    def spawn(self, kernel_name=None, cwd=None):
        # if manager not set
        if self.manager is None: 
            raise Exception("dizest manager not connected")

        # previous options
        if kernel_name is None: kernel_name = self.kernel_name
        if cwd is None: cwd = self.cwd
        spawner = self.manager.spawner(self.id(), kernel_name=kernel_name, cwd=cwd, workflow=self)
        kernelspec = self.manager.kernelspec(kernel_name)
        if kernelspec is not None:
            spawner.kernelspec = kernelspec
        if cwd is not None:
            spawner.cwd = cwd
        try:
            self.kill()
        except:
            pass
        
        self.start()
        
        spawner.update()

        return self

    # spawner functions
    def connect(self, spawner):
        self.spawner = spawner
        spawner.workflow = self

    def start(self):
        if self.spawner is None:
            raise Exception("Spawner is not connected")
        self.spawner.start()

    def stop(self):
        if self.spawner is None:
            raise Exception("Spawner is not connected")
        self.spawner.stop()
    
    def restart(self):
        if self.spawner is None:
            raise Exception("Spawner is not connected")
        self.spawner.restart()
    
    def kill(self):
        if self.spawner is None:
            raise Exception("Spawner is not connected")
        self.spawner.kill()

    def status(self):
        if self.spawner is None:
            return 'stop'
        return self.spawner.status

    def current(self):
        if self.spawner is None:
            raise Exception("Spawner is not connected")
        return self.spawner.current

    def run(self):
        if self.spawner is None:
            return False

        flows = self.flows()
        for flow_id in flows:
            flow = self.flow(flow_id)
            if flow.active():
                self.spawner.run(flow_id)
        
        return True