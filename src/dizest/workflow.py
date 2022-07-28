from dizest import util

class App:
    def __init__(self, workflow, package):
        self.package = package
        self.workflow = workflow

    def id(self):
        return self.package['id']

    def code(self):
        return self.package['code']

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

    def run(self):
        if self.workflow.spawner is None:
            return False
        flow_id, code, inputs, outputs = self.data()
        self.workflow.spawner.run(flow_id, code, inputs, outputs)
        return True

class Workflow:
    def __init__(self, package):
        required = ['id', 'apps', 'flow']
        for req in required:
            if req not in package:
                raise Exception(f"`{req}` not defined")
        self.package = package
        self.spawner = None

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

    # spawner functions
    def start(self):
        if self.spawner is None:
            return False
        self.spawner.start()
        return True

    def stop(self):
        if self.spawner is None:
            return False
        self.spawner.stop()
    
    def restart(self):
        if self.spawner is None:
            return False
        self.spawner.restart()
    
    def kill(self):
        if self.spawner is None:
            return False
        self.spawner.kill()

    def connect(self, spawner):
        self.spawner = spawner
        spawner.workflow = self

    def disconnect(self):
        if self.spawner is not None:
            self.spawner.workflow = None
        self.spawner = None
