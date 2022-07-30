from dizest import util
from abc import *
import sys
import os
import subprocess
import multiprocessing as mp
import random
import socketio
import requests
import json
import signal
import time

class Log:
    def __init__(self, id):
        self.id = id
        self._data = []
    
    def append(self, log):
        self._data.append(log)
    
    def clear(self):
        del self._data
        self._data = []

    def __getitem__(self, attr):
        return self._data[attr]

class Flow:
    def __init__(self, id=None):
        self.id = id        
        if id is None: 
            self._data = dict()
            return

        self._data = None
        self.status = 'ready'
        self.index = ''
        self.log = Log(id)

    def __getattr__(self, attr):
        if self.id is None:
            if attr not in self._data:
                self._data[attr] = Flow(attr)
            return self._data[attr]
        return None

    def __getitem__(self, attr):
        if self.id is None:
            if attr not in self._data:
                self._data[attr] = Flow(attr)
            return self._data[attr]
        return None

    def __call__(self, attr):
        if self.id is None:
            if attr not in self._data:
                self._data[attr] = Flow(attr)
            return self._data[attr]
        return None
    
class BaseSpawner(metaclass=ABCMeta):
    def __init__(self, id, kernelspec, manager, cwd=None):
        self.name = 'base'
        self.kernel = kernelspec['name']
        self.id = id
        self.kernelspec = kernelspec
        self.manager = manager
        self.cwd = cwd
        self.flow = Flow()
        
        self.status = 'stop'
        self.current = None
        self.workflow = None

    def init(self):
        self.flow = Flow()

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def restart(self):
        pass

    @abstractmethod
    def kill(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def run(self, flow_id, code, inputs, outputs):
        pass

class SimpleSpawner(BaseSpawner):
    def __init__(self, id, kernelspec, manager, cwd=None):
        super().__init__(id, kernelspec, manager, cwd=cwd)
        self.name = 'simple'
        self.process = None
        self._request()

    def _request(self):
        try:
            self.request.process.kill()
        except:
            pass
        self.request = util.std.stdClass()
        def reqthread(q):
            def sigterm_handler(_signo, _stack_frame):
                exit(0)
            signal.signal(signal.SIGTERM, sigterm_handler)
            signal.signal(signal.SIGABRT, sigterm_handler)
            signal.signal(signal.SIGINT, sigterm_handler)

            while True:
                try:
                    msg = json.loads(q.recv())

                    for i in range(5):
                        try:
                            url = msg['url']
                            data = msg['data']
                            requests.post(url, data=data, timeout=None)
                            break
                        except Exception as e1:
                            time.sleep(3)
                except Exception as e2:
                    pass

        sender, receiver = mp.Pipe()
        self.request.process = mp.Process(target=reqthread, args=(receiver,))
        self.request.sender = sender
        self.request.process.start()

    def _send(self, data):
        sender = self.request.sender
        data = json.dumps(data, default=util.string.json_default)
        sender.send(data)

    def start(self):
        if self.process is not None:
            return 

        id = self.id
        kernelspec = self.kernelspec
        cwd = self.cwd
        manager = self.manager

        port = random.randrange(10000, 60000)
        while util.os.port(port):
            port = random.randrange(10000, 60000)

        KERNELSPEC_PATH = kernelspec['path']
        LIBSPEC_PATH = os.path.join(os.path.dirname(__file__), 'spec')
        cmd = kernelspec['cmd'].replace("$EXECUTABLE", sys.executable).replace("$KERNELSPEC_PATH", KERNELSPEC_PATH).replace("$LIBSPEC_PATH", LIBSPEC_PATH).replace("$PORT", str(port))
        cmd = cmd.split(" ")

        env = os.environ.copy()
        env['SPAWNER_ID'] = id
        env['DIZEST_API'] = manager.api()

        if cwd is not None:
            self.process = subprocess.Popen(cmd, shell=False, cwd=cwd, env=env)
        else:
            self.process = subprocess.Popen(cmd, shell=False, env=env)

        self.port = port
        self.status = 'ready'

    def kill(self):
        self.init()
        self._request()
        self.process.terminate()
        self.process = None
        self.status = 'stop'

    def restart(self):
        self.kill()
        self.start()

    def stop(self):
        self._request()
        self.process.send_signal(signal.SIGABRT)

    def run(self, flow_id, code, inputs, outputs):
        if self.process is None:
            raise Exception("Spawner is not started")

        self.flow(flow_id).log.clear()

        port = self.port
        id = self.id

        data = dict()
        data['url'] = f"http://127.0.0.1:{port}/run"
        data['data'] = {"id": flow_id, "code": code, "inputs": json.dumps(inputs, default=util.string.json_default), "outputs": json.dumps(outputs, default=util.string.json_default)}

        self._send(data)

        self.manager.send(id=id, flow_id=flow_id, mode='flow.status', data='pending')
        self.manager.send(id=id, flow_id=flow_id, mode='flow.index', data='')
