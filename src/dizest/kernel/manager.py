from dizest import util
from dizest.kernel import spawner
from dizest.workflow import Workflow
import sys
import os
import subprocess
import random
import socketio
import requests

class Manager:
    def __init__(self, path=None, host="127.0.0.1", broker=None, spawner_class=spawner.SimpleSpawner):
        self._data = util.std.stdClass()
        
        self._data.basepath = path
        self._data.broker = broker
        
        self._data.server = util.std.stdClass()
        self._data.server.host = host
        self._data.server.port = None
        self._data.server.process = None
        self._data.server.api = None

        self._data.spawner_class = spawner_class
        self._data.spawners = dict()
        self._data.workflows = dict()

        self._data.kernel = util.std.stdClass()
        self._data.kernel.specs = dict()
        self._data.kernel.names = ['base']

        self._data.kernel.specs['base'] = dict()
        self._data.kernel.specs['base']['path'] = ''
        self._data.kernel.specs['base']['name'] = 'base'
        self._data.kernel.specs['base']['cmd'] = "$EXECUTABLE $LIBSPEC_PATH/python/kernel.py $PORT"

        self.set_path(path)

    # save log
    def send(self, **data):
        try:
            requests.post(self.api() + '/log', data=data)
        except:
            pass
        return self

    # setter
    def set_broker(self, broker):
        self._data.broker = broker
        return self

    def set_host(self, host):
        self._data.server.host = host
        return self

    def set_spawner_class(self, spawner_class):
        self._data.spawner_class = spawner_class
        return self

    def set_path(self, path):
        if path is None:
            return self
        self._data.basepath = path

        self._data.kernel = util.std.stdClass()
        self._data.kernel.specs = dict()
        self._data.kernel.names = ['base']

        self._data.kernel.specs['base'] = dict()
        self._data.kernel.specs['base']['path'] = ''
        self._data.kernel.specs['base']['name'] = 'base'
        self._data.kernel.specs['base']['cmd'] = "$EXECUTABLE $LIBSPEC_PATH/python/kernel.py $PORT"

        fs = util.os.storage(path)
        specs = fs.list()
        for spec in specs:
            if fs.isdir(spec):
                try:
                    kernelspec = fs.read.json(os.path.join(spec, 'kernel.json'))
                    kernelspec['path'] = fs.abspath(spec)
                    self._data.kernel.specs[kernelspec['name']] = kernelspec
                    self._data.kernel.names.append(kernelspec['name'])
                except:
                    pass
        return self

    # manager server api url
    def api(self):
        return self._data.server.api

    def spawners(self):
        return [x for x in self._data.spawners]

    def workflows(self):
        return [x for x in self._data.workflows]

    def workflow_by_id(self, workflow_id):
        if workflow_id in self._data.workflows:
            return self._data.workflows[workflow_id]
        return None

    def kernelspecs(self):
        return self._data.kernel.names

    def kernelspec(self, kernel_name):
        spawner_class = self._data.spawner_class
        kernelspecs = self._data.kernel.specs
        if kernel_name not in kernelspecs:
            return None
        return kernelspecs[kernel_name]

    def process(self):
        return self._data.server.process

    def is_running(self):
        if self._data.server.process is not None:
            return True
        return False

    # manager server start
    def start(self):
        if self._data.server.process is not None:
            return self

        path = self._data.basepath
        host = self._data.server.host

        executable = sys.executable
        server = os.path.join(os.path.dirname(__file__), 'server.py')

        port = random.randrange(3000, 9999)
        while util.os.port(port):
            port = random.randrange(3000, 9999)

        self._data.server.process = subprocess.Popen([executable, server, str(port)], shell=False)
        self._data.server.port = port
        self._data.server.api = f'http://{host}:{port}'

        sio = socketio.Client()
        @sio.on('log')
        def on_message(data):
            try:
                SPAWNER_ID = data['id']
                if 'flow_id' not in data:
                    FLOW_ID = None
                else:    
                    FLOW_ID = data['flow_id']
                MODE = data['mode']
                data = data['data']
                
                spawner = self.spawner(SPAWNER_ID)
                if spawner is None: return
                
                if MODE == 'flow.log' and FLOW_ID is not None:
                    spawner.flow(FLOW_ID).log.append(data)
                
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
                    except:
                        pass

                if self._data.broker is not None:
                    self._data.broker(spawner, FLOW_ID, MODE, data)
            except Exception as e:
                pass
        
        while True:
            try:
                sio.connect(self._data.server.api)
                break
            except:
                pass
        
        return self

    def restart(self):
        try:
            self.stop()
        except:
            pass
        self.start()
        return self

    # manager server stop
    def stop(self):
        # kill all spawners process
        for key in self._data.spawners:
            try:
                self._data.spawners[key].kill()
            except:
                pass
        
        # kill manager server
        self._data.server.process.terminate()

        # init instance
        self._data.spawners = dict()
        self._data.server.port = None
        self._data.server.process = None
        self._data.server.api = util.std.stdClass()
        self._data.server.api = None

        return self
    
    # call spawner
    def spawner(self, id, kernel_name=None, cwd=None, workflow=None):
        spawner_class = self._data.spawner_class
        kernelspecs = self._data.kernel.specs
        if id in self._data.spawners: 
            return self._data.spawners[id]
        if kernel_name not in kernelspecs:
            return None
        kernelspec = kernelspecs[kernel_name]
        self._data.spawners[id] = spawner_class(id, kernelspec, self, cwd=cwd)
        if workflow is not None:
            workflow.connect(self._data.spawners[id])
        return self._data.spawners[id]

    # workflow loader
    def workflow(self, package):
        workflow = Workflow(package)
        wpid = workflow.id()
        if wpid in self._data.workflows:
            return self._data.workflows[wpid]
        workflow.manager = self
        self._data.workflows[wpid] = workflow
        return workflow