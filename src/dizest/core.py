from dizest import util
import os
import multiprocessing as mp
import time
import json
import traceback
import sys
import requests

class Dizest:
    def __init__(self):
        self.data = dict()
        self._output = dict()
    
    def set(self, **kwargs):
        for key in kwargs:
            self.data[key] = kwargs[key]
    
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
    
    def get_output(self):
        return self._output

class App:
    def __init__(self, package):
        self.package = package
    
    def get(self, key, default=None):
        if key in self.package:
            return self.package[key]
        return default

class Flow:
    def __init__(self, workflow, package):
        self.workflow = workflow
        self._id = package['id']
        self._app_id = package['app_id']
        self._values = package['data']
        self._inputs = dict()
        self._outputs = dict()
        for key in package['inputs']:
            try:
                self._inputs[key] = []
                for con in package['inputs'][key]['connections']:
                    self._inputs[key].append({"flow_id": con['node'], "name": con['input']})
            except:
                pass

        for key in package['outputs']:
            try:
                self._outputs[key] = []
                for con in package['outputs'][key]['connections']:
                    self._outputs[key].append({"flow_id": con['node'], "name": con['output']})
            except:
                pass
    
    def app(self):
        workflow = self.workflow
        return workflow.app(self._app_id)
    
    def id(self):
        return self._id
    
    def values(self):
        return self._values
    
    def inputs(self):
        return self._inputs
    
    def outputs(self):
        return self._outputs
    
    def run(self, **kwargs):
        flow_id = self.id()
        workflow = self.workflow
        index = workflow.get_status('index', 0)
        index = index + 1

        workflow.set_status('index', index)
        workflow.set_status('current', flow_id)

        self.set_status('index', index)
        self.set_status('code', 0)
        self.set_status('status', 'running')

        inputs_define = self.inputs()
        inputs = dict()
                
        is_runnable = True
        required_process_flow = []
        for name in inputs_define:
            inputs[name] = dict()
            rows = inputs_define[name]
            for item in rows:
                output = self.workflow.flow(item['flow_id']).get_output(item['name'])
                if output is None:
                    required_process_flow.append(item['flow_id'])
                    is_runnable = False
                else:
                    inputs[name][item['flow_id']] = output
        
        if is_runnable == False:
            self.set_status('status', 'error')
            self.set_status('code', 1)
            self.set_status('message', required_process_flow)
            return
        
        values = self.values()
        
        dizest = Dizest()
        dizest.set(inputs=inputs, values=values)
        
        # run process
        app = self.app()
        app_code = app.get("code")

        env = dict()
        env['dizest'] = dizest
        local_env = dict()
        
        try:
            exec(app_code, env, local_env)
        except Exception as e:
            self.set_status('status', 'error')
            self.set_status('code', 2)
            self.set_status('message', str(e))
            return
        
        output = dizest.get_output()
        for key in output:
            self.set_output(key, output[key])

        self.set_status('code', 0)
        self.set_status('status', 'finish')

    def get_status(self, name, default=None):
        flow_id = self.id()
        try: return dict(self.workflow._status)[f"{flow_id}::{name}"]
        except: return default
    
    def set_status(self, name, value):
        flow_id = self.id()
        self.workflow._status[f"{flow_id}::{name}"] = value

        try:
            if self.workflow.status_changed_api is not None:
                wpid = self.workflow.id()
                fid = self.id()
                requests.get(self.workflow.status_changed_api + f"?workflow_id={wpid}&flow_id={fid}")
        except Exception as e:
            pass

    def get_output(self, name, default=None):
        flow_id = self.id()
        try: return dict(self.workflow._output)[f"{flow_id}::{name}"]
        except: return default
    
    def set_output(self, name, value):
        flow_id = self.id()
        self.workflow._output[f"{flow_id}::{name}"] = value
        
class Kernel:
    def __init__(self, workflow):
        self.workflow = workflow
        self.init()
    
    # overrides
    def run(self, flow_id):
        pass

    def stop(self):
        pass

    def start(self):
        pass
    
    # built-ins
    def init(self):
        self.p = None
        self.q = None
        
    def _process(self, q):
        states = dict()
        q.put(os.getpid())
        
        while True:
            try:
                msg = q.get()
                action = msg['action']
                if action == 'run':
                    flow_id = msg['data']
                    self.run(flow_id)
            except Exception as e:
                pass

    def _start(self):
        if self.p is not None:
            raise Exception("Process already running")
        self.q = mp.Queue()
        self.p = mp.Process(target=self._process, args=[self.q])
        self.p.start()
        self.pid = self.q.get()

    def action(self, action, pdata=None):
        if self.p is None:
            self.init()
            raise Exception("no running process")
        if self.is_alive() == False:
            self.init()
            raise Exception("no running process")
        
        data = dict()
        data['action'] = action
        data['data'] = pdata
        self.q.put(data)
        
    def _stop(self):
        try:
            self.p.kill()
            self.p.join()
        except:
            pass
        
        processstate = self.is_alive()
        if processstate:
            return False

        self.init()
        return True

    def is_alive(self):
        if self.p is None:
            return False
        return self.p.is_alive()
    
    def __del__(self):
        self.stop()

class SingleThreadKernel(Kernel):
    def run(self, flow_id):
        self.workflow.flow(flow_id).run()

    def stop(self):
        self._stop()

    def start(self):
        self._start()

class MultiThreadKernel(Kernel):
    def run(self, flow_id):
        def process(workflow, flow_id):
            workflow.flow(flow_id).run()
        p = mp.Process(target=process, args=[self.workflow, flow_id])
        p.start()
        p.join()
        p.kill()
        
    def stop(self):
        self._stop()

    def start(self):
        self._start()

class Workflow:
    def __init__(self, package, kernel=MultiThreadKernel, status_changed_api=None):
        self.kernel_class = kernel
        self._id = package['id']
        self._package = mp.Manager().dict()
        self._package['flow'] = package['flow']
        self._package['apps'] = package['apps']

        self.status_changed_api = status_changed_api

        self._global_status = mp.Manager().dict()
        self._status = mp.Manager().dict()
        self._output = mp.Manager().dict()
        self.kernel = self.kernel_class(self)
        self.kernel.start()
        
    def __del__(self):
        self.kernel.stop()

    def update(self, package):
        self._package['flow'] = package['flow']
        self._package['apps'] = package['apps']
    
    def id(self):
        return self._id
    
    def app(self, app_id):
        return App(self._package['apps'][app_id])
    
    def flows(self):
        return [x for x in self._package['flow']]
    
    def flow(self, flow_id=None):
        if flow_id is None:
            flow_id = self.get_status("current")
        if flow_id is None:
            return None
        flow = self._package['flow'][flow_id]
        flow = Flow(self, flow)
        return flow
    
    def start(self):
        self.kernel.start()

    def restart(self):
        self.stop()
        self.kernel.start()
        
    def stop(self, flow_id=None):
        if flow_id is None:
            self._global_status = mp.Manager().dict()
            self._status = mp.Manager().dict()
            self._output = mp.Manager().dict()
        else:
            flow = self.flow(flow_id)
            flow.set_status('status', 'error')
            flow.set_status('code', 3)
            flow.set_status('message', "stopped")

            flows = self.flows()
            for fid in flows:
                flow = self.flow(fid)
                status = flow.get_status('status')
                if status in ['pending']:
                    flow.set_status('status', 'ready')
                    flow.set_status('code', 0)
                    flow.set_status('message', "")

        self.kernel.stop()
        
    def run(self, flow_id):
        flow = self.flow(flow_id)
        flow.set_status('code', 0)
        flow.set_status('status', 'pending')
        self.kernel.action('run', flow_id)
        return self.flow(flow_id)
        
    def get_status(self, name, default=None):
        try: return dict(self._global_status)[name]
        except: return default
    
    def set_status(self, name, value):
        self._global_status[name] = value
