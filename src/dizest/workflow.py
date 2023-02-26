from dizest import util
from dizest.core.app import App
from dizest.core.flow import Flow
from dizest.core.logger import Logger
from dizest.core.renderer import Renderer

class Workflow:
    def __init__(self, namespace, package=None):
        if namespace is None:
            raise Exception("Namespace not defined")
        self.index = 0
        self.__namespace__ = namespace
        self.__trigger__ = dict()
        self.__renderer__ = Renderer().render
        self.load(package)

    def namespace(self):
        return self.__namespace__

    def id(self):
        return self.__package__['id']

    def app(self, app_id, package=None):
        app = None
        if app_id not in self.__apps__:
            if package is not None:
                self.__package__['apps'][app_id] = package
                self.__apps__[app_id] = App(self, app_id)
                self.__apps__[app_id].clean()
            else:
                app = None
        else:
            app = self.__apps__[app_id]
            if package is not None:
                app.update(**package)
        return app

    def delete_app(self, app_id):
        del self.__package__['apps'][app_id]
        del self.__apps__[app_id]
        return self

    def flows(self):
        flows = []
        for flow_id in self.__package__['flow']:
            flows.append(self.__package__['flow'][flow_id])
        flows.sort(key=lambda x: x['order'])
        return [x['id'] for x in flows]

    def flow(self, flow_id, package=None):
        flow = None
        if flow_id not in self.__flows__:
            if package is not None:
                package['id'] = flow_id
                self.__package__['flow'][flow_id] = package
                self.__flows__[flow_id] = Flow(self, flow_id)
                self.__flows__[flow_id].clean()
                flow = self.__flows__[flow_id]
            else:
                flow = None
        else:
            flow = self.__flows__[flow_id]
            if package is not None:
                flow.update(**package)
        return flow

    def delete_flow(self, flow_id):
        del self.__package__['flow'][flow_id]
        del self.__flows__[flow_id]
        return self

    def on(self, eventname, trigger):
        self.__trigger__[eventname] = trigger
        return self

    def renderer(self, renderer):
        self.__renderer__ = renderer
        return self

    def update(self, **kwargs):
        disallowed = ['id', 'apps', 'flow']
        for key in kwargs:
            if key in disallowed:
                continue
            self.__package__[key] = kwargs[key]

    def status(self):
        flows = self.flows()
        for flow_id in flows:
            flow = self.flow(flow_id)
            status = flow.status()
            if status in ['pending', 'running']:
                return 'running'
        return 'idle'

    def run(self, threaded=True):
        flows = self.flows()
        for flow_id in flows:
            flow = self.flow(flow_id)
            if flow.active():
                flow.run(threaded=threaded)

    def stop(self):
        flows = self.flows()
        for flow_id in flows:
            flow = self.flow(flow_id)
            flow.stop()

    def to_dict(self):
        return self.__package__

    def __event__(self, flow_id, eventname, value):
        namespace = self.namespace()
        if eventname in self.__trigger__: 
            util.fn.call(self.__trigger__[eventname], namespace=namespace, flow_id=flow_id, eventname=eventname, event=eventname, value=value, workflow_id=self.id())
        if "*" in self.__trigger__: 
            util.fn.call(self.__trigger__["*"], namespace=namespace, flow_id=flow_id, eventname=eventname, event=eventname, value=value, workflow_id=self.id())

    def load(self, package):
        self.logger = Logger()
        self.logger.onchange = self.__event__
        self.cache = dict()
        self.__apps__ = dict()
        self.__flows__ = dict()
        self.__package__ = None
        if package is None:
            return
        
        required = ['id', 'apps', 'flow']
        for req in required:
            if req not in package:
                raise Exception(f"{req} not defined")
        self.__package__ = package

        # load app instance
        apps = package['apps']
        for app_id in apps:
            self.__apps__[app_id] = App(self, app_id)
            self.__apps__[app_id].clean()

        # load flow instance
        flows = package['flow']
        for flow_id in flows:
            self.__flows__[flow_id] = Flow(self, flow_id)
            self.__flows__[flow_id].clean()

    def load_file(self, filepath):
        storage = util.os.storage()
        package = storage.read.json(filepath, dict())
        self.load(package)