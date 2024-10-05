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
        