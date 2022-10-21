from dizest import util
import requests
import pypugjs
from pypugjs.ext import jinja
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
        kwargs["url"] = self.workflow.spawner.uri() + "/api/" + self.id() + "/" + fnname
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
        pug = jinja.Compiler(pug, **pugconfig).compile()

        head = app.get("head", "")
        head = pypugjs.Parser(head)
        head = head.parse()
        head = jinja.Compiler(head, **pugconfig).compile()

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
        except Exception as e:
            css = ""

        _head = ""
        _body = ""
        if 'head' in kwargs: _head = kwargs['head']
        if 'body' in kwargs: _body = kwargs['body']

        view = f"<!DOCTYPE html><html><head>{head}{_head}{css}</head><body>{pug}{_body}{js}</body></html>"
        return view

class Workflow:
    def __init__(self, package):
        required = ['id', 'apps', 'flow']
        for req in required:
            if req not in package:
                raise Exception(f"{req} not defined")
        self.package = package
        self.spawner = None
        self.server = None
        self.kernel_name = None

    @classmethod
    def load(cls, package):
        if isinstance(package, str):
            fs = util.os.storage(".")
            package = fs.read.json(package)
        return cls(package)

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
        return self.kernel_name

    def update(self, package):
        self.package = package
        if self.spawner is not None:
            self.spawner.update()

    def spawn(self, kernel_name=None):
        if self.server is None: 
            raise Exception("dizest server not connected")
        server = self.server

        cwd = server.config("cwd")

        # load kernelspec
        if kernel_name is None: 
            kernel_name = self.kernel_name
        kernelspec = server.kernelspec(kernel_name)

        # generate spawner
        if self.spawner is None:
            spawner_class = server.config('spawner_class')
            kernelspec = server.kernelspec(kernel_name)
            self.spawner = spawner_class(workflow=self, kernelspec=kernelspec, cwd=cwd, mode="kernel")

        # update kernelspec
        if kernelspec is not None:
            self.spawner.kernelspec = kernelspec
            self.kernel_name = kernel_name
        
        # kill previous spawner
        try:
            self.kill()
        except Exception as e:
            pass
        
        # start spawner
        self.start()
        
        # spawner update
        self.spawner.update()

        return self

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

    def run(self):
        if self.spawner is None:
            return False

        flows = self.flows()
        for flow_id in flows:
            flow = self.flow(flow_id)
            if flow.active():
                self.spawner.run(flow_id)
        
        return True
