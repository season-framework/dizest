import os
from dizest import util
from dizest.base.config import BaseConfig
from dizest.core.app import App
from dizest.core.flow import Flow
from dizest.core.renderer import Renderer
from dizest.core.runnable import Runnable

class Config(BaseConfig):
    DEFAULT_VALUES = {
        'cwd': (None, os.getcwd()),
        'max_log_size': (int, 50),
        'event': (dict, {
            '*': None,
            'workflow.status': None,
            'flow.status': None,
            'flow.index': None,
            'log.append': None,
            'log.clear': None
        })
    }

class Workflow:
    render = Renderer()
    index = 0

    def __init__(self, package, **kwargs):
        self.config = Config(kwargs)
        self.load(package)
        self.run = Runnable(self)

    def load(self, package):
        if type(package) == str:
            storage = util.os.storage()
            package = storage.read.json(package, dict())
        
        required = ['apps', 'flow']
        for req in required:
            if req not in package:
                raise Exception(f"{req} not defined")
        
        self.__package__ = package

        return self

    def to_dict(self):
        return self.__package__
    
    def apps(self):
        apps = []
        for app_id in self.__package__['apps']:
            apps.append(app_id)
        return apps
    
    def app(self, app_id):
        if app_id in self.__package__['apps']:
            return App(self, app_id)
        return None

    def flows(self):
        flows = []
        for flow_id in self.__package__['flow']:
            flows.append(self.flow(flow_id))
        return flows
    
    def flow(self, flow_id):
        if flow_id in self.__package__['flow']:
            return Flow(self, flow_id)
        return None
    
    def on(self, name, fn):
        self.config.event[name] = fn

    def onchanged(self, flow, event_name, value):
        if event_name in self.config.event and self.config.event[event_name] is not None:
            self.config.event[event_name](flow, event_name, value)
        if '*' in self.config.event and self.config.event['*'] is not None:
            self.config.event["*"](flow, event_name, value)
    
    def spec(self):
        flows = self.flows()

        requested = dict()
        outputs = dict()

        for flow in flows:
            inputs = flow.app().inputs()
            for inputitem in inputs:
                if inputitem['type'] == 'output':
                    key = inputitem['name'] 
                    if flow.id() not in requested:
                        requested[flow.id()] = dict()
                    requested[flow.id()][key] = None

            inputs = flow.inputs()
            for key in inputs:
                if inputs[key]['type'] == 'output':
                    if len(inputs[key]['data']) == 0:
                        if flow.id() not in requested:
                            requested[flow.id()] = dict()
                        requested[flow.id()][key] = None
                    else:
                        if key in requested[flow.id()]:
                            del requested[flow.id()][key]
                        if len(requested[flow.id()]) == 0:
                            del requested[flow.id()]
                        for item in inputs[key]['data']:
                            if item[0] not in outputs:
                                outputs[item[0]] = dict()
                            outputs[item[0]][item[1]] = flow.id()
            
            output_data = flow.app().outputs()
            for key in output_data:
                if flow.id() not in outputs:
                    outputs[flow.id()] = dict()
                if key not in outputs[flow.id()]:
                    outputs[flow.id()][key] = None

        _outputs = dict()
        for flow_id in outputs:
            for out in outputs[flow_id]:
                if outputs[flow_id][out] is None:
                    if flow_id not in _outputs:
                        _outputs[flow_id] = []
                    _outputs[flow_id].append(out)
        outputs = _outputs
        return requested, outputs