from dizest.core.dizesti import DizestInstance
from dizest import util
import multiprocessing as mp
import os
import time
import threading
import traceback
import psutil

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

    def status(self):
        return self.logger.status()

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
            vname = val['name']
            if vtype == 'output':
                cons = [[x['node'], x['input']] for x in flow['inputs'][vname]['connections']]
                inputs[vname] = {"type": vtype, "data": cons}
            elif vtype == 'variable':
                if vname in flow['data']:
                    inputs[vname] = ({"type": vtype, "data": flow['data'][vname]})
        return inputs

    def run(self, threaded=True):
        flow = self
        renderer = self.workflow.__renderer__
        logger = self.logger
        status = logger.status()
        if status not in ['idle', 'error']:
            return False

        logger.set_status("pending")

        def runningThread():
            logger.set_status("running")

            def display(*args):
                args = list(args)
                for i in range(len(args)):
                    try:
                        args[i] = renderer(args[i])
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
                        active = _pflow.active()
                        pstatus = _pflow.status()
                        if active:
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
                    time.sleep(1)

                data = dict()
                data['flow_id'] = flow.id()
                data['inputs'] = inputs

                dizesti = DizestInstance(flow, data)
                flow.workflow.cache[flow.id()] = dizesti

                env = dict()
                env['dizest'] = dizesti
                env['print'] = display
                env['display'] = display

                exec(code, env)

                flow.workflow.index = flow.workflow.index + 1
                logger.set_status("idle")
                logger.set_index(flow.workflow.index)

            except SystemExit:
                pass

            except:
                stderr = traceback.format_exc()
                logger.set_status("error")
                logger.set_index(-1)
                logger.set_log(stderr.strip())

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
