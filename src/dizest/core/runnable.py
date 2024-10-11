import traceback
import os
import time
from dizest import util

class FlowInstance:
    def __init__(self, runnable, flow, data):
        self.timestamp = time.time()
        self.runnable = runnable
        self.workflow = runnable.workflow
        self.process = None
        self.flow = flow
        self.data = data
        self.output_data = dict()
        self.cache = dict(index=-1, log=[], status='idle')
    
    def onchanged(self, event_name, value):
        self.workflow.onchanged(self.flow.id(), event_name, value)

    def update(self, flow, data):
        self.flow = flow
        self.data = data

    def status(self, value=None):
        if value is not None:
            if value not in  ['idle', 'pending', 'running', 'error', 'ready']:
                value = 'idle'
            self.cache['status'] = value
            self.onchanged("flow.status", value)
            wpstatus = self.runnable.status()
            self.workflow.onchanged(None, "workflow.status", wpstatus)

        value = self.cache['status']
        if value not in  ['idle', 'pending', 'running', 'error', 'ready']:
            value = 'idle'
        return value

    def index(self, value=None):
        if value is not None:
            self.cache['index'] = value
            self.onchanged("flow.index", value)
        return self.cache['index']
    
    def log(self, value=None):
        if value is not None:
            self.cache['log'].append(value)
            self.cache['log'] = self.cache['log'][-self.workflow.config.max_log_size:]
            self.onchanged("log.append", value)
        return self.cache['log']
    
    def clear(self):
        self.cache['log'].clear()
        self.onchanged("log.clear", True)

    def input(self, name, default=None):
        try:
            cache = self.runnable.cache
            inputs = self.flow.inputs()
            if name not in inputs:
                return default

            itype = inputs[name]['type']
            ivalue = inputs[name]['data']

            if itype == 'variable':
                inputtype = None
                if 'inputtype' in inputs[name]: 
                    inputtype = inputs[name]['inputtype']
                
                if type(ivalue) == bool:
                    return ivalue

                if ivalue is not None and len(ivalue) > 0:
                    try:
                        if inputtype == 'number':
                            ivalue = float(ivalue)
                    except:
                        pass
                    return ivalue

                return default
            
            res = None
            timestamp = 0
            for iv in ivalue:
                fid = iv[0]
                oname = iv[1]
                if fid not in cache:
                    continue

                if timestamp < cache[fid].timestamp:
                    timestamp = cache[fid].timestamp
                    linked_output = cache[fid].output_data
                    if oname in linked_output:
                        res = linked_output[oname]
                    else:
                        res = None

            return res
        except Exception as e:
            pass
        
        return default

    def inputs(self, name):
        try:
            cache = self.runnable.cache
            res = []
            inputs = self.flow.inputs()
            if name not in inputs:
                return res
            
            itype = inputs[name]['type']
            ivalue = inputs[name]['data']

            if itype == 'variable':
                return res
            
            for iv in ivalue:
                fid = iv[0]
                oname = iv[1]
                if fid not in cache:
                    res.append(None)
                    continue

                linked_output = cache[fid].output_data
                if oname in linked_output:
                    res.append(linked_output[oname])
                else:
                    res.append(None)
            
            return res
        except Exception as e:
            pass

        return []

    def output(self, *args, **kwargs):
        if len(args) == 1:
            name = args[0]
            if name in self.output_data:
                return self.output_data[name]
            return None

        if len(args) >= 2:
            name = args[0]
            value = None
            if len(args) > 1:
                value = args[1]
            
            self.output_data[name] = value
            return value
        
        for name in kwargs:
            value = kwargs[name]
            self.output_data[name] = value

    def result(self, name, value, **kwargs):
        try:
            value = self.workflow.render(value, **kwargs)
        except Exception as e:
            value = str(value)
        self.onchanged("result", dict(name=name, value=value))

    def drive(self, *path):
        cwd = self.flow.workflow.config.cwd
        cwd = os.path.join(cwd, *path)
        return util.os.storage(cwd)
    
    def binding(self, flask=None, path=None):
        class Binding:
            def __init__(self, parent, flask, path):
                self.clear = parent.clear
                self.input = parent.input
                self.inputs = parent.inputs
                self.output = parent.output
                self.result = parent.result
                self.drive = parent.drive
                if flask is not None:
                    self.run = parent.run
                    self.stop = parent.stop
                    self.response = util.web.Response(flask)
                    self.request = util.web.Request(flask, path)
        return Binding(self, flask, path)

    def run(self, threaded=True, **params):
        flow = self.flow
        flow_instance = self
        inputs = self.flow.inputs()

        # 프로세스 시작
        flow_instance.status("pending")
        flow_instance.index(-1)
        
        def runningThread():
            try:
                # flow instance 최신화
                data = dict()
                data['flow_id'] = flow.id()
                flow_instance.update(flow, data)
                
                # 이전 생행 flow 상태 확인 및 대기
                previous_flows = flow.previous()

                while True:
                    isactive = True
                    for previous_flow_id in previous_flows:
                        previous_flow = self.workflow.flow(previous_flow_id)
                        previous_flow_instance = self.runnable.instance(previous_flow)

                        previous_index = previous_flow_instance.index()
                        previous_status = previous_flow_instance.status()

                        if previous_status not in ['idle']:
                            isactive = False

                        if previous_index <= 0:
                            isactive = False
                        
                        if previous_index == -2 or previous_status in ['stop', 'error']:
                            flow_instance.status("idle")
                            flow_instance.index(-2)
                            flow_instance.log("Stop")
                            raise SystemExit()
                    
                    if isactive:
                        break
                    time.sleep(0.1)
                
                # 프로세스 실행
                flow_instance.status("running")
                flow_instance.clear()
                
                def display(*args, **kwargs):
                    args = list(args)
                    for i in range(len(args)):
                        try:
                            args[i] = self.workflow.render(args[i], **kwargs)
                        except Exception as e:
                            args[i] = str(args[i])
                    log = " ".join(args)
                    flow_instance.log(log.strip())
                
                app = flow.app()
                code = app.code()

                binding = flow_instance.binding()
                binding.__input__ = binding.input
                def _input(name, default=None):
                    if name in params:
                        return params[name]
                    return binding.__input__(name, default=default)
                binding.input = _input

                env = dict()
                env['__name__'] = os.path.join(self.workflow.config.cwd)
                env['dizest'] = binding
                env['print'] = display
                env['display'] = display
                env['flow'] = flow
                env['workflow'] = self.workflow

                for key in inputs:
                    env[key] = flow_instance.input(key)
                
                for key in params:
                    env[key] = params[key]

                flow_instance.output_data = dict()
                os.chdir(self.workflow.config.cwd)

                code = "import os\nimport sys\nsys.path.append(os.getcwd())\n" + code

                exec(code, env)

                for key in app.outputs():
                    if key in flow_instance.output_data:
                        continue
                    if key in env:
                        flow_instance.output(key, env[key])

                self.workflow.index = self.workflow.index + 1
                flow_instance.status("idle")
                flow_instance.index(self.workflow.index)

            except SystemExit:
                return
            except:
                stderr = traceback.format_exc().replace("\n", "<br>").replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;").replace(" ", "&nbsp;").strip()
                stderr = f"<div class='text-red'>{stderr}</div>"
                flow_instance.status("error")
                flow_instance.index(-1)
                flow_instance.log(stderr)
                return
            return

        process = util.os.Thread(target=runningThread)
        process.start()

        flow_instance.process = process

        if threaded == False:
            process.join()
        
        return process

    def stop(self):
        if self.process is None:
            return True
        try:
            self.process.stop()
        except:
            pass
        self.status("idle")
        self.index(-2)
        self.log("Stop")
        self.process = None
        return True
    
    def api(self, flask, fnname, path):
        flow = self.flow
        flow_instance = self

        def display(*args, **kwargs):
            args = list(args)
            for i in range(len(args)):
                try:
                    args[i] = self.workflow.render(args[i], **kwargs)
                except Exception as e:
                    args[i] = str(args[i])
            log = " ".join(args)
            self.onchanged("flow.api", log.strip())

        try:
            app = flow.app()
            code = app.api()
            
            data = dict()
            data['flow_id'] = flow.id()

            env = dict()
            env['dizest'] = flow_instance.binding(flask, path)
            env['print'] = display
            env['display'] = display
            env['flow'] = flow
            env['workflow'] = self.workflow

            code = "import os\nimport sys\nsys.path.append(os.getcwd())\n" + code

            exec(code, env)

            env[fnname]()
        except util.web.ResponseException as e1:
            code, response = e1.get_response()
            return response, code
        except Exception as e2:
            stderr = traceback.format_exc()
            self.onchanged("flow.api", stderr)
            return {"code": 500, "data": stderr}, 500

        return {"code": 404}, 404

class Runnable:
    def __init__(self, workflow):
        self.workflow = workflow
        self.cache = dict()

    def status(self):
        flows = self.workflow.flows()
        is_pending = False
        for flow in flows:
            flow_instance = self.instance(flow)
            status = flow_instance.status()
            if status == 'running':
                return 'running'
            if status == 'pending':
                is_pending = True
        if is_pending:
            return 'pending'
        return 'idle'
    
    def is_runnable(self):
        return self.status() not in ['running', 'pending']

    def instance(self, flow):
        if flow.id() in self.cache:
            return self.cache[flow.id()]
        data = dict()
        data['flow_id'] = flow.id()
        flow_instance = FlowInstance(self, flow, data)
        self.cache[flow.id()] = flow_instance
        return self.cache[flow.id()]
    
    def sync(self):
        workflow = self.workflow
        
        target = []
        for flow_id in self.cache:
            if flow_id not in workflow.to_dict()['flow']:
                target.append(flow_id)

        res = []
        for flow_id in target:
            del self.cache[flow_id]
            res.append("delete flow cache: " + flow_id)

        return res

    def __call__(self, flow=None, threaded=True, **kwargs):
        if flow is None:
            if self.is_runnable() == False:
                return
            flows = self.workflow.flows()
            for flow in flows:
                if flow.active():
                    flow_instance = self.instance(flow)
                    flow_instance.output_data = dict()
                    flow_instance.cache = dict(index=-1, log=[], status='idle')
            for flow in flows:
                if flow.active():
                    flow_instance = self.instance(flow)
                    flow_instance.status("ready")
                    flow_instance.run(threaded=threaded, **kwargs)
            return

        flow_instance = self.instance(flow)
        return flow_instance.run(threaded=threaded, **kwargs)
        
    def stop(self, flow=None):
        if flow is not None:
            self.instance(flow).stop()
            return
        
        flows = self.workflow.flows()
        for flow in flows:
            flow_instance = self.instance(flow)
            flow_instance.stop()
        self.cache.clear()
        self.workflow.index = 0