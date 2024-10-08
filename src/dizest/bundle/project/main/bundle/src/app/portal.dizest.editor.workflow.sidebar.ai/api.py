import requests
import json

DIZEST_INSTANCE_REF_CODE = """
아래 코드는 현재 개발 창에서 사용 할 수 있는 dizest 객체에 대한 코드인데, FlowInstance 객체에서 binding 함수가 dizest 객체를 생성하는 코드야.

```python
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
                if ivalue is not None and len(ivalue) > 0:
                    try:
                        if inputtype == 'number':
                            ivalue = float(ivalue)
                    except:
                        pass
                    return ivalue
                else:
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

    def result(self, name=None):
        if name is None:
            for key in self.output_data:
                self.onchanged("result." + key, self.output_data[key])
            return

        if name in self.output_data:
            self.onchanged("result." + name, self.output_data[name])

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
                        
                        if previous_status not in ['idle', 'error']:
                            isactive = False
                        if previous_index <= 0:
                            isactive = False
                        
                        if previous_index == -2:
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

                env = dict()
                env['__name__'] = os.path.join(self.workflow.config.cwd)
                env['dizest'] = flow_instance.binding()
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
        
        return self

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
```
"""

struct = wiz.model("portal/dizest/struct")
config = struct.config
config.acl()
fs = wiz.fs()
llmconfig = fs.read.json("dizest.json", {})
keys = ['use_ai', 'llm_gateway', 'llm_api_key', 'llm_model']
for key in keys:
    if key not in llmconfig or llmconfig[key] == '' or llmconfig[key] is None:
        llmconfig[key] = config[key]
        
def llmRequest(text, context, stream=True):
    api_host = llmconfig["llm_gateway"]
    api_key = llmconfig["llm_api_key"]
    model = llmconfig["llm_model"]

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": DIZEST_INSTANCE_REF_CODE
                    }
                ]
            },
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": context
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": text
                    }
                ]
            }
        ],
        "max_tokens": 4096,
        "stream": stream
    }

    response = requests.post(api_host + "/chat/completions", headers=headers, json=payload, stream=stream)
    return response    

def request():
    query = wiz.request.query("query", True)
    context = wiz.request.query("context", "")
    stream = wiz.request.query("stream", None)

    if stream is None: stream = False
    else: stream = True

    resp = llmRequest(query, context, stream=stream)

    logger = print

    if stream:
        def generate():
            for chunk in resp.iter_lines():
                if chunk:
                    try:
                        text = chunk.decode('utf-8').strip()
                        if text.startswith("data: "):
                            text = text[len("data: "):]
                        text = json.loads(text)
                        text = text['choices'][0]['delta']['content']
                        yield text
                    except:
                        pass

        Response = wiz.response._flask.Response
        response = Response(generate(), content_type='text/event-stream')
        wiz.response.response(response)

    resp = resp.json()
    try:
        return resp["choices"][0]['message']["content"]
    except:
        return resp["error"]['message']

    wiz.response.status(200, resp)
