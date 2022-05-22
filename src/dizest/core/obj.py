import copy
import os
import multiprocessing as mp
import time
import json
import traceback
import sys
import requests
import pypugjs
import sass

from dizest import util
from dizest.core import kernel

class Instance(util.std.stdClass):
    def __init__(self, flow):
        self.flow = flow
        self.data = dict()
        self._output = dict()
        self.response = util.response.response()

        inputs, values = flow.inputs()
        self.data['inputs'] = inputs
        self.data['values'] = values

    def storage(self, mode='local'):
        cwd = self.flow.workflow.opts.cwd
        return util.os.storage(cwd, root=False, rw=True)

    def input(self, name, default=None, id=None):
        try:
            if name in self.data['inputs']:
                keys = [x for x in self.data['inputs'][name]]
                if id is None: id = keys[0]
                return self.data['inputs'][name][id]
        except Exception as e:
            pass
        try:
            return self.data['values'][name]
        except:
            return default
        
    def inputs(self, name):
        try:
            return self.data['inputs'][name]
        except:
            return dict()
    
    def output(self, name, value):
        self._output[name] = value

class App:
    def __init__(self, package):
        self.package = package
    
    def get(self, key, default=None):
        if key in self.package:
            return self.package[key]
        return default

    def set(self, **kwargs):
        for key in kwargs:
            self.package[key] = kwargs[key]

class Flow:
    class Status:
        def __init__(self, flow):
            self.flow = flow

        def get(self, key, default=None):
            try:
                fid = self.flow.id()
                fs = self.flow.workflow.cache(os.path.join("flow", fid))
                return fs.read.pickle(key, default)
            except:
                return default
        
        def set(self, **kwargs):
            fid = self.flow.id()
            for key in kwargs:
                value = kwargs[key]
                fs = self.flow.workflow.cache(os.path.join("flow", fid))
                fs.write.pickle(key, value)

        def send(self):
            try:
                if self.flow.workflow.opts.api is not None:
                    wpid = self.flow.workflow.id()
                    fid = self.flow.id()
                    requests.post(self.flow.workflow.opts.api, {"mode": "flowstat", "workflow_id": wpid, "flow_id": fid})
            except Exception as e:
                pass

        def clear(self):
            fid = self.flow.id()
            fs = self.flow.workflow.cache(os.path.join("flow", fid))
            fs.remove()

    class Define:
        def __init__(self, flow):
            self.flow = flow

        def data(self):
            return self.flow.package['data']

        def inputs(self):
            return self.flow.package['inputs']

        def outputs(self):
            return self.flow.package['outputs']

    class Output:
        def __init__(self, flow):
            self.flow = flow
            self.workflow = flow.workflow

        def set(self, key, value):
            flow = self.flow
            workflow = self.workflow
            flow_id = flow.id()
            if flow_id not in workflow.output_manager:
                workflow.output_manager[flow_id] = dict()
            workflow.output_manager[flow_id][key] = value
        
        def get(self, key):
            flow = self.flow
            workflow = self.workflow
            flow_id = flow.id()
            try:
                return workflow.output_manager[flow_id][key]
            except:
                return None

        def clear(self):
            flow = self.flow
            workflow = self.workflow
            flow_id = flow.id()
            try:
                del workflow.output_manager[flow_id]
            except:
                pass

        def load(self):
            flow = self.flow
            workflow = self.workflow
            fid = flow.id()
            fs = workflow.cache(os.path.join("output"))
            workflow.output_manager[fid] = fs.read.pickle(fid, dict())

        def save(self):
            flow = self.flow
            workflow = self.workflow
            fid = flow.id()
            if fid not in workflow.output_manager:
                return
            fs = workflow.cache(os.path.join("output"))
            fs.write.pickle(fid, workflow.output_manager[fid])

    def __init__(self, workflow, flow_id):
        self.workflow = workflow
        self.package = copy.deepcopy(workflow.package['flow'][flow_id])
        
        def parser(package, target):
            targets = target + 's'
            tmp = dict()
            for key in package[targets]:
                try:
                    tmp[key] = []
                    for con in package[targets][key]['connections']:
                        tmp[key].append({"flow_id": con['node'], "name": con[target]})
                except Exception as e:
                    pass
            return tmp

        self.package['inputs'] = parser(self.package, 'input')
        self.package['outputs'] = parser(self.package, 'output')


        self.define = self.Define(self)
        self.status = self.Status(self)
        self.output = self.Output(self)

    def logger(self, *args, color=94):
        if self.workflow.opts.api is None:
            print(*args)
            return
        workflow_id = self.workflow.id()
        flow_id = self.id()
        tag = f"[dizest]"
        log_color = color
        args = list(args)
        for i in range(len(args)): 
            args[i] = str(args[i])
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        logdata = f"\033[{log_color}m[{timestamp}]{tag}\033[0m " + " ".join(args)
        requests.post(self.workflow.opts.api, {"mode": "stdout", "data": logdata, "workflow_id": workflow_id, "flow_id": flow_id})

    def app(self):
        workflow = self.workflow
        return workflow.app(self.package['app_id'])

    def instance(self):
        return Instance(self)

    def id(self):
        return self.package['id']

    def inputs(self):
        flow = self
        workflow = flow.workflow
        flow_id = flow.id()
        use_sample = workflow.opts.isdev

        values = flow.define.data()
        inputs_define = flow.define.inputs()
        inputs = dict()

        if use_sample == False:
            required_process_flow = []
            for name in inputs_define:
                inputs[name] = dict()
                rows = inputs_define[name]
                for item in rows:
                    prev_fid = item['flow_id']
                    prev_key = item['name']
                    prev_flow = workflow.flow(prev_fid)
                    output = prev_flow.output.get(prev_key)
                    inputs[name][prev_fid] = output
        else:
            sample = flow.app().get("sample", "")
            env = dict()
            env['data'] = dict()
            exec(sample, env)
            output = env['data']
            for name in inputs_define:
                inputs[name] = dict()
                if name in output:
                    inputs[name]['sample'] = output[name]
                    del output[name]
            values = output
        
        return inputs, values

    def run(self, **env):
        flow = self
        flow_id = flow.id()
        workflow = flow.workflow
        cwd = workflow.cwd()
        if os.path.isdir(cwd) == False:
            os.makedirs(cwd)
        os.chdir(cwd)

        index = workflow.status.get('index', 0)
        index = index + 1
        workflow.status.set(index=index, current=flow_id)
        flow.status.set(index=index, code=0, status='running', message='')
        flow.status.send()

        # process
        app = flow.app()
        app_code = app.get("code")

        # build api instance
        env['print'] = flow.logger
        env['display'] = flow.logger
        instance = self.instance()
        env['dizest'] = instance
        
        flow.output.clear()

        local_env = dict()
        try:
            exec(app_code, env, local_env)
        except Exception as e:
            stderr = traceback.format_exc()
            flow.logger(stderr)
            flow.status.set(code=2, status='error', message=str(e))
            flow.status.send()
            return

        output = instance._output
        for key in output:
            flow.output.set(key, output[key])

        flow.status.set(code=0, status='finish', message="")
        flow.status.send()

        return self
    
    def api(self, fnname):
        flow = self
        flow_id = flow.id()
        workflow = flow.workflow

        cwd = workflow.cwd()
        if os.path.isdir(cwd) == False:
            os.makedirs(cwd)

        app = flow.app()
        api = app.get("api")

        env['print'] = flow.logger
        env['display'] = flow.logger
        instance = Instance(flow)
        env['dizest'] = instance

        try:
            local_env = dict()
            exec(api, env, local_env)
            local_env[fnname]()
        except dizest_core.util.response.ResponseException as e:
            return True, e
        except Exception as e:
            return False, e        
        return False, None

    def render(self):
        flow = self
        app = flow.app()
        pug = app.get("pug")

        pugconfig = dict()
        pugconfig['variable_start_string'] = '{$'
        pugconfig['variable_end_string'] = '$}'

        pug = pypugjs.Parser(pug)
        pug = pug.parse()
        pug = pypugjs.ext.jinja.Compiler(pug, **pugconfig).compile()
        
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

        view = f"{pug}{js}{css}"
        return view

class Workflow(util.std.stdClass):
    class Status:
        def __init__(self, workflow):
            self.workflow = workflow

        def get(self, key, default=None):
            try:
                fs = self.workflow.cache("workflow")
                return fs.read.pickle(key, default)
            except:
                return default
        
        def set(self, **kwargs):
            for key in kwargs:
                value = kwargs[key]
                fs = self.workflow.cache("workflow")
                fs.write.pickle(key, value)

        def send(self):
            try:
                if self.workflow.opts.api is not None:
                    wpid = self.workflow.id()
                    requests.post(self.workflow.opts.api, {"mode": "wpstat", "workflow_id": wpid})
            except Exception as e:
                pass

        def clear(self):
            fs = self.workflow.cache()
            fs.remove()
            
    class Options(util.std.stdClass):
        def __getattr__(self, attr):
            obj = self.get(attr)
            if type(obj) == dict:
                return stdClass(obj)
            if obj is None:
                if attr == 'api': return None
                if attr == 'cwd': return os.getcwd()
                if attr == 'cache': return os.path.join(os.getcwd(), ".dizest", "cache")
                if attr == 'isdev': return False
                if attr == 'kernel_class': return kernel.Single
                if attr == 'kernel_mode': return "spawn"
                if attr == 'kernel_env': return sys.executable
            return obj

    def __init__(self, package, **opts):
        self.opts = self.Options(**opts)
        self.package = package
        self.status = self.Status(self)
        self.output_manager = dict()

    def cwd(self):
        return self.opts.cwd
    
    def cache(self, path=""):
        return util.os.storage(os.path.join(self.opts.cache, self.id(), path))

    def update(self, package, **opts):
        self.package['flow'] = package['flow']
        self.package['apps'] = package['apps']

        for key in opts:
            self.opts[key] = opts[key]

    def info(self):
        data = dict()
        pkg = dict()
        pkg['id'] = self.package['id']
        pkg['apps'] = self.package['apps']
        pkg['flow'] = self.package['flow']

        def clean(app, key):
            try:
                del app[key]
            except:
                pass
            return app

        for app_id in pkg['apps']:
            pkg['apps'][app_id] = clean(pkg['apps'][app_id], "logo")
            pkg['apps'][app_id] = clean(pkg['apps'][app_id], "featured")
            pkg['apps'][app_id] = clean(pkg['apps'][app_id], "description")
            pkg['apps'][app_id] = clean(pkg['apps'][app_id], "user_id")
            pkg['apps'][app_id] = clean(pkg['apps'][app_id], "title")
            pkg['apps'][app_id] = clean(pkg['apps'][app_id], "version")
            pkg['apps'][app_id] = clean(pkg['apps'][app_id], "mode")
            pkg['apps'][app_id] = clean(pkg['apps'][app_id], "visibility")

        data['package'] = pkg
        data['opts'] = dict(self.opts)
        return data

    def id(self):
        return self.package['id']
        
    def app(self, app_id):
        return App(self.package['apps'][app_id])
    
    def flows(self):
        return [x for x in self.package['flow']]

    def flow(self, flow_id=None):
        if flow_id is None:
            flow_id = self.status.get("current")
        if flow_id is None:
            return None
        return Flow(self, flow_id)

    def kernel(self):
        kernel = self.opts.kernel_class(self)
        return kernel