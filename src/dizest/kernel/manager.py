from dizest import util
from dizest.kernel import spawner
import sys
import os
import subprocess
import random
import socketio
import requests

class Manager:
    def __init__(self, path, host="127.0.0.1", broker=None, spawner_class=spawner.SimpleSpawner):
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

        self._data.kernel = util.std.stdClass()
        self._data.kernel.specs = dict()
        self._data.kernel.names = []

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
        
        self.start()

    # save log
    def send(self, **data):
        try:
            requests.post(self.api() + '/log', data=data)
        except:
            pass

    # set broker
    def set_broker(self, broker):
        self._data.broker = broker

    # manager server api url
    def api(self):
        return self._data.server.api

    # manager server start
    def start(self):
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
                FLOW_ID = data['flow_id']
                MODE = data['mode']
                data = data['data']
                
                spawner = self.spawner(SPAWNER_ID)
                if spawner is None: return
                if MODE == 'log' and FLOW_ID is not None:
                    spawner.log[FLOW_ID].append(data)
                if MODE == 'status' and FLOW_ID is not None:
                    spawner.status[FLOW_ID].status = data
                if MODE == 'index' and FLOW_ID is not None:
                    spawner.status[FLOW_ID].index = data

                if self._data.broker is not None:
                    self._data.broker(spawner, FLOW_ID, MODE, data)
            except:
                pass
        
        while True:
            try:
                sio.connect(self._data.server.api)
                break
            except:
                pass
        
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
    def spawner(self, id, kernel_name=None, cwd=None):
        spawners = self._data.spawners
        spawner_class = self._data.spawner_class
        kernelspecs = self._data.kernel.specs

        if id in spawners: return spawners[id]
        if kernel_name not in kernelspecs:
            return None

        kernelspec = kernelspecs[kernel_name]

        self._data.spawners[id] = spawner_class(id, kernelspec, self, cwd=cwd)
        return self._data.spawners[id]