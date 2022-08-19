from dizest import spawner
from dizest import util
from dizest.workflow import Workflow
import sys
import os
import time
import subprocess
import random
import socketio
import requests
import platform
import threading

class DriveAPI:
    def __init__(self, server):
        self.server = server

    def __request__(self, fnname, **kwargs):
        kwargs["url"] = self.server.drive().uri() + "/drive/" + fnname
        kwargs["allow_redirects"] = False
        return requests.request(**kwargs)

    def ls(self, path):
        if len(path) > 0:
            if path[0] == "/": 
                path = path[1:]
        return self.__request__(f"ls/{path}", method="GET", timeout=3)

    def create(self, path, data):
        if len(path) > 0:
            if path[0] == "/": 
                path = path[1:]
        return self.__request__(f"create/{path}", method="POST", data=data, timeout=3)

    def rename(self, path, data):
        if len(path) > 0:
            if path[0] == "/": 
                path = path[1:]
        return self.__request__(f"rename/{path}", method="POST", data=data, timeout=3)

    def remove(self, path, data):
        if len(path) > 0:
            if path[0] == "/": 
                path = path[1:]
        return self.__request__(f"remove/{path}", method="POST", data=data, timeout=3)
    
    def upload(self, path, **kwargs):
        if len(path) > 0:
            if path[0] == "/": 
                path = path[1:]
        return self.__request__(f"upload/{path}", **kwargs)

    def download(self, path):
        if len(path) > 0:
            if path[0] == "/": 
                path = path[1:]
        return self.__request__(f"download/{path}", method="GET")

class Server:
    def __init__(self, host="127.0.0.1", broker=None, spawner_class=spawner.SimpleSpawner, log_limit=0, cwd=None, user=None, executable=None):
        self._data = util.std.stdClass()

        self._data.config = util.std.stdClass()
        self._data.config.log_limit = log_limit
        self._data.config.spawner_class = spawner_class
        self._data.config.broker = broker
        self._data.config.host = host
        self._data.config.cwd = cwd
        self._data.config.user = user
        self._data.config.executable = executable
        
        self._data.server = util.std.stdClass()
        self._data.server.drive = None
        self._data.server.terminal = dict()
        self._data.server.process = None
        self._data.server.port = None
        self._data.server.api = None

        self._data.kernel = util.std.stdClass()
        self._data.kernel.specs = dict()
        self._data.kernel.names = []

        self._data.workflows = dict()

        self.drive_api = DriveAPI(self)

    def drive(self):
        return self._data.server.drive

    # config
    def config(self, *args, **kwargs):
        # set config
        for key in kwargs:
            self._data.config[key] = kwargs[key]
        
        # get config
        if len(args) == 1:
            key = args[0]
            if key in self._data.config:
                return self._data.config[key]
            else:
                return None
        
        res = []
        for key in args:
            if key in self._data.config:
                res.append(self._data.config[key])
            else:
                res.append(None)
        return tuple(res)

    # kernelspec
    def kernelspecs(self):
        return self._data.kernel.names

    def kernelspec(self, kernel_name):
        kernelspecs = self._data.kernel.specs
        if kernel_name not in kernelspecs:
            return None
        return kernelspecs[kernel_name]

    def set_kernelspec(self, name=None, **data):
        if 'kernel' not in data: raise Exception("kernelspec must contains `kernel`")
        data['name'] = name
        if 'name' not in data: raise Exception("kernelspec must contains `name`")
        if 'title' not in data: data['title'] = name
        self._data.kernel.specs[name] = data
        self._data.kernel.names.append(name)
        return self._data.kernel.specs[name]
    
    def clear_kernelspec(self):
        self._data.kernel.specs = dict()
        self._data.kernel.names = []

    # server api url
    def api(self):
        return self._data.server.api

    def process(self):
        return self._data.server.process

    def is_running(self):
        if self._data.server.process is not None:
            return True
        return False

    def send(self, **data):
        try:
            requests.post(self.api() + '/log', data=data)
        except Exception as e:
            pass
        return self

    def start(self):
        if self._data.server.process is not None:
            return self

        host = self._data.config.host
        executable = self.config('executable')
        if executable is None:
            executable = sys.executable
        server = os.path.join(os.path.dirname(__file__), 'kernel', 'server.py')

        port = random.randrange(3000, 9999)
        while util.os.port(port):
            port = random.randrange(3000, 9999)

        self._data.server.process = subprocess.Popen([executable, server, str(port)], shell=False)
        self._data.server.port = port
        self._data.server.api = f'http://{host}:{port}'

        scache = []
        sio = socketio.Client()

        @sio.on('log')
        def on_message(data):
            try:
                WORKFLOW_ID = data['id']
                if 'flow_id' not in data:
                    FLOW_ID = None
                else:    
                    FLOW_ID = data['flow_id']
                MODE = data['mode']
                data = data['data']
                
                workflow = self.workflow(WORKFLOW_ID)
                if workflow is None: return
                spawner = workflow.spawner
                if spawner is None: return
                
                if MODE == 'flow.log' and FLOW_ID is not None:
                    spawner.flow(FLOW_ID).log.append(data)
                
                if MODE == 'flow.log.clear' and FLOW_ID is not None:
                    spawner.flow(FLOW_ID).log.clear()
                
                if MODE == 'flow.status' and FLOW_ID is not None:
                    spawner.flow(FLOW_ID).status = data
                    if data == 'running': 
                        spawner.current = FLOW_ID
                    elif data == 'finish': 
                        spawner.current = None

                if MODE == 'flow.index' and FLOW_ID is not None:
                    spawner.flow(FLOW_ID).index = data

                if MODE == 'kernel.status':
                    spawner.status = data
                    try:
                        if data == 'error':
                            for key in spawner.flow._data:
                                if spawner.flow(key).status != 'pending': 
                                    continue
                                spawner.flow(key).status = 'ready'
                    except Exception as e:
                        pass

                args = dict()
                args['workflow_id'] = workflow.id()
                args['flow_id'] = FLOW_ID
                args['mode'] = MODE
                args['data'] = data
                scache.append(args)
            except Exception as e:
                pass
        
        while True:
            try:
                sio.connect(self._data.server.api)
                break
            except Exception as e:
                pass

        # checking thread
        def polling():
            while True:
                try:
                    if len(scache) > 0:
                        if self._data.config.broker is not None:
                            util.fn.call(self._data.config.broker, logs=scache)
                    scache.clear()
                except Exception as e:
                    pass
                time.sleep(1)

        th = threading.Thread(target=polling)
        th.start()

        # start drive spawner
        spawner_class = self.config('spawner_class')
        cwd = self.config("cwd")
        self._data.server.drive = spawner_class(server=self, cwd=cwd, mode="drive")
        self._data.server.drive.start()

        return self

    def stop(self):
        # kill all spawners process
        for key in self._data.workflows:
            try:
                self._data.workflows[key].kill()
            except Exception as e:
                pass
        
        # kill server
        self._data.server.drive.terminate()
        self._data.server.process.terminate()

        # init instance
        self._data.server.port = None
        self._data.server.process = None
        self._data.server.api = None

        return self

    def restart(self):
        try:
            self.stop()
        except Exception as e:
            pass
        self.start()
        return self

    # workflow
    def workflows(self):
        return [x for x in self._data.workflows]

    def workflow(self, package):
        if isinstance(package, dict):
            workflow_id = package['id']
            if workflow_id in self._data.workflows:
                return self._data.workflows[workflow_id]
            
            workflow = Workflow(package)
            workflow_id = workflow.id()
            workflow.server = self
            self._data.workflows[workflow_id] = workflow
            return workflow
        else:
            return self.workflow_by_id(package)

    def workflow_by_id(self, workflow_id):
        if workflow_id in self._data.workflows:
            return self._data.workflows[workflow_id]
        return None
