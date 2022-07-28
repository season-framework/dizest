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

class Log:
    def __init__(self, id=None):
        self.id = id
        if id is None: self._data = dict()
        else: self._data = []
    
    def append(self, log):
        if id is None: return
        self._data.append(log)
    
    def clear(self):
        del self._data
        if self.id is None: self._data = dict()
        else: self._data = []

    def __getattr__(self, attr):
        if self.id is None:
            if attr not in self._data:
                self._data[attr] = Log(attr)
            return self._data[attr]

    def __getitem__(self, attr):
        if self.id is None:
            if attr not in self._data:
                self._data[attr] = Log(attr)
            return self._data[attr]
        return self._data[attr]

class Status:
    def __init__(self, id=None):
        self.id = id
        self._data = None
        if id is None: self._data = dict()
        self.status = 'pending'
        self.index = ''

    def __getattr__(self, attr):
        if self.id is None:
            if attr not in self._data:
                self._data[attr] = Status(attr)
            return self._data[attr]
        return None

    def __getitem__(self, attr):
        if self.id is None:
            if attr not in self._data:
                self._data[attr] = Status(attr)
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
        self.log = Log()
        self.status = Status()
        self.is_running = False
        self.workflow = None

    def init(self):
        self.log = Log()
        self.status = Status()

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
                    url = msg['url']
                    data = msg['data']
                    requests.post(url, data=data, timeout=None)
                except Exception as e:
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
        self.is_running = True

    def kill(self):
        self.init()
        self._request()
        self.process.terminate()
        self.process = None
        self.is_running = False

    def restart(self):
        self.kill()
        self.start()

    def stop(self):
        self._request()
        self.process.send_signal(signal.SIGABRT)

    def run(self, flow_id, code, inputs, outputs):
        self.log[flow_id].clear()        
        port = self.port
        manager = self.manager
        id = self.id

        data = dict()
        data['url'] = f"http://127.0.0.1:{port}/run"
        data['data'] = {"id": flow_id, "code": code, "inputs": json.dumps(inputs, default=util.string.json_default), "outputs": json.dumps(outputs, default=util.string.json_default)}

        self._send(data)

        manager.send(id=id, flow_id=flow_id, mode='status', data='ready')
        manager.send(id=id, flow_id=flow_id, mode='index', data='')
