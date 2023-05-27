from dizest.core.dizesti import DizestInstance
from dizest import util
import time
import traceback

class Flow:
    def __init__(self, workflow, flow_id):
        self.workflow = workflow
        self.package = workflow.__package__['flow'][flow_id]
        self.logger = workflow.logger.load(flow_id)
        self.process = None
        del self.package['log']

    # update
    def update(self, **kwargs):
        for key in kwargs:
            self.package[key] = kwargs[key]
    
    def clean(self):
        allowed = ['id', 'name', 'data', 'inputs', 'app_id' ,'pos_x', 'pox_y', 'order', 'inactive', 'meta']
        keys = [key for key in self.package]
        for key in keys:
            if key not in allowed:
                del self.package[key]
        return self

    # getter
    def id(self):
        return self.package['id']

    def name(self):
        return self.package['name']

    def pos_x(self):
        return self.package['pos_x']

    def pos_y(self):
        return self.package['pos_y']

    def order(self):
        return self.package['order']

    def active(self):
        if 'inactive' not in self.package:
            return True
        if self.package['inactive']:
            return False
        return True
    
    def app_id(self):
        return self.package['app_id']

    def app(self):
        return self.workflow.app(self.package['app_id'])

    def status(self, status=None):
        if status in ['idle', 'error', 'pending', 'running', 'ready']:
            self.logger.set_status(status)
        status = self.logger.status()
        return status

    def is_runnable(self):
        return self.status() in ['idle', 'error', 'ready']

    def index(self):
        return self.logger.index()

    def log(self):
        return self.logger.log()

    def inputs(self):
        flow = self.package
        app = self.app()
        appinput = app.inputs()
        inputs = dict()
        for val in appinput:
            vtype = val['type']
            inputtype = val['inputtype'] if 'inputtype' in val else None
            vname = val['name']
            if vtype == 'output':
                cons = [[x['node'], x['input']] for x in flow['inputs'][vname]['connections']]
                inputs[vname] = {"type": vtype, "data": cons}
            elif vtype == 'variable':
                if vname in flow['data']:
                    inputs[vname] = ({"type": vtype, "data": flow['data'][vname], "inputtype": inputtype})
                else:
                    inputs[vname] = ({"type": vtype, "data": None, "inputtype": inputtype})
        return inputs
    
    # TODO: find next flows
    def next(self):
        pass

    def api(self, flask, fnname, path):
        flow = self
        logger = self.logger

        def display(*args):
            args = list(args)
            for i in range(len(args)):
                args[i] = str(args[i])
            log = " ".join(args)
            logger.set_api(log.strip())

        try:
            app = self.app()
            code = app.api()
            inputs = flow.inputs()
            
            data = dict()
            data['flow_id'] = flow.id()
            data['inputs'] = inputs

            if flow.id() in flow.workflow.cache:
                dizesti = flow.workflow.cache[flow.id()]
                dizesti.__bind__(flask, path)
                dizesti.__changed__(flow, data)
            else:
                dizesti = DizestInstance(flow, data, flask=flask, path=path)
                flow.workflow.cache[flow.id()] = dizesti
                
            env = dict()
            env['dizest'] = dizesti
            env['print'] = display
            env['display'] = display
            env['flow'] = flow
            env['workflow'] = flow.workflow

            exec(code, env)

            env[fnname]()
        except util.web.ResponseException as e1:
            code, response = e1.get_response()
            return response, code
        except Exception as e2:
            stderr = traceback.format_exc()
            logger.set_api(stderr)
            return {"code": 500, "data": stderr}, 500

        return {"code": 404}, 404

    def run(self, threaded=True):
        flow = self
        renderer = self.workflow.__renderer__
        logger = self.logger

        if self.is_runnable() == False:
            return False

        logger.set_status("pending")
        logger.set_index(-1)

        def runningThread():
            def display(*args, **kwargs):
                args = list(args)
                for i in range(len(args)):
                    try:
                        args[i] = renderer(args[i], **kwargs)
                    except Exception as e:
                        args[i] = str(args[i])
                log = " ".join(args)
                logger.set_log(log.strip())

            try:
                app = flow.app()
                code = app.code()
                inputs = flow.inputs()
                previous_flow = []
                for key in inputs:
                    if inputs[key]['type'] == 'output':
                        links = inputs[key]['data']
                        for link in links:
                            if link[0] not in previous_flow:
                                previous_flow.append(link[0])

                while True:
                    isactive = True
                    for pflow in previous_flow:
                        _pflow = flow.workflow.flow(pflow)
                        pindex = _pflow.index()
                        pstatus = _pflow.status()
                        
                        if pstatus not in ['idle', 'error']:
                            isactive = False
                        if pindex <= 0:
                            isactive = False
                        
                        if pindex == -2:
                            logger.set_status("idle")
                            logger.set_index(-2)
                            logger.set_log("Stop")
                            raise SystemExit()
                    if isactive:
                        break
                    time.sleep(0.1)

                logger.set_status("running")
                flow.logger.clear_log()

                data = dict()
                data['flow_id'] = flow.id()
                data['inputs'] = inputs

                if flow.id() in flow.workflow.cache:
                    dizesti = flow.workflow.cache[flow.id()]
                    dizesti.__unbind__()
                    dizesti.__changed__(flow, data)
                else:
                    dizesti = DizestInstance(flow, data)
                    flow.workflow.cache[flow.id()] = dizesti

                env = dict()
                env['dizest'] = dizesti
                env['print'] = display
                env['display'] = display
                env['flow'] = flow
                env['workflow'] = flow.workflow

                for key in inputs:
                    env[key] = dizesti.input(key)

                exec(code, env)

                for key in self.app().outputs():
                    if key in dizesti._output:
                        continue
                    if key in env:
                        dizesti.output(key, env[key])

                flow.workflow.index = flow.workflow.index + 1
                logger.set_status("idle")
                logger.set_index(flow.workflow.index)

            except SystemExit:
                pass

            except:
                stderr = traceback.format_exc().replace("\n", "<br>").replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;").replace(" ", "&nbsp;").strip()
                stderr = f"<div class='text-red'>{stderr}</div>"
                logger.set_status("error")
                logger.set_index(-1)
                logger.set_log(stderr)

        process = util.os.Thread(target=runningThread)
        process.start()
        self.process = process

        if threaded == False:
            process.join()

        return True
    
    def stop(self):
        if self.process is None:
            return True
        try:
            self.process.stop()
        except:
            pass

        logger = self.logger
        logger.set_status("idle")
        logger.set_index(-2)
        logger.set_log("Stop")

        self.process = None

        return True
