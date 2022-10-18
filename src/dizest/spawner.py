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
import psutil

class Log:
    def __init__(self, id, limit=0):
        self.id = id
        self._data = []
        self.limit = limit
    
    def append(self, log):
        self._data.append(log)
        self._data = self._data[-self.limit:]
    
    def clear(self):
        del self._data
        self._data = []

    def __getitem__(self, attr):
        return self._data[attr]

class Flow:
    def __init__(self, workflow, id=None):
        self.id = id        
        self.workflow = workflow
        
        if id is None: 
            self._data = dict()
            return

        self._data = None
        self.status = 'ready'
        self.index = ''
        self.log = Log(id, limit=workflow.server.config('log_limit'))

    def __getattr__(self, attr):
        if self.id is None:
            if attr not in self._data:
                self._data[attr] = Flow(self.workflow, attr)
            return self._data[attr]
        return None

    def __getitem__(self, attr):
        if self.id is None:
            if attr not in self._data:
                self._data[attr] = Flow(self.workflow, attr)
            return self._data[attr]
        return None

    def __call__(self, attr):
        if self.id is None:
            if attr not in self._data:
                self._data[attr] = Flow(self.workflow, attr)
            return self._data[attr]
        return None
    
class BaseSpawner(metaclass=ABCMeta):
    def __init__(self, server=None, workflow=None, kernelspec=None, cwd=None, mode="kernel"):
        self.name = 'base'
        self.mode = mode
        self.kernelspec = kernelspec
        self.cwd = cwd

        self.status = 'stop'
        self.current = None
        self.workflow = workflow

        if self.workflow is not None:
            self.server = self.workflow.server
            self.flow = Flow(self.workflow)
        else:
            self.server = server

        self.user = self.server.config("user")

    def init(self):
        if self.workflow is not None:
            self.flow = Flow(self.workflow)

    def storage(self):
        return util.os.storage(self.cwd)

    def start(self):
        if self.mode == 'kernel':
            self.kernel_start()
        elif self.mode == 'drive':
            self.drive_start()

    def kill(self):
        self.init()
        if self.mode == 'kernel':
            self.kernel_kill()
        elif self.mode == 'drive':
            self.drive_kill()

    def restart(self):
        self.kill()
        self.start()

    def run(self, *args, **kwargs):
        if self.mode == 'kernel':
            self.kernel_run(*args, **kwargs)
        else:
            raise Exception("not support run")

    def stop(self):
        if self.mode == 'kernel':
            self.kernel_stop()
        else:
            raise Exception("not support stop")

    def update(self):
        if self.mode == 'kernel':
            self.kernel_update()
        else:
            raise Exception("not support update")

    @abstractmethod
    def uri(self):
        pass

    @abstractmethod
    def terminal_start(self):
        pass

    @abstractmethod
    def terminal_kill(self):
        pass

    @abstractmethod
    def drive_start(self):
        pass

    @abstractmethod
    def drive_kill(self):
        pass

    @abstractmethod
    def kernel_start(self):
        pass

    @abstractmethod
    def kernel_kill(self):
        pass

    @abstractmethod
    def kernel_stop(self):
        pass

    @abstractmethod
    def kernel_run(self, flow_id, code, inputs, outputs):
        pass

    @abstractmethod
    def kernel_update(self):
        pass

class SimpleSpawner(BaseSpawner):
    def __init__(self, server=None, workflow=None, kernelspec=None, cwd=None, mode="kernel"):
        super().__init__(server=server, workflow=workflow, kernelspec=kernelspec, cwd=cwd, mode=mode)
        self.name = 'simple'
        self.process = None
        self._uri = None
        self._request()

    def _request(self):
        try:
            self.request.process.terminate()
        except Exception as e:
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
                            res = requests.post(url, data=data, timeout=None)
                            break
                        except Exception as e1:
                            time.sleep(5)
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

    def _kill(self):
        self._request()
        self.process.terminate()
        self.process = None
        self.status = 'stop'
        self.port = None
        self._uri = None

    # override abstract kernel methods
    def uri(self):
        return self._uri
    
    def kernel_start(self):
        if self.process is not None:
            return 

        workflow = self.workflow
        server = workflow.server

        kernelspec = self.kernelspec
        cwd = self.cwd

        port = random.randrange(10000, 60000)
        while util.os.port(port):
            port = random.randrange(10000, 60000)

        LIBSPEC_PATH = os.path.join(os.path.dirname(__file__), 'kernel', 'spec')
        cmd = kernelspec['kernel'].replace("$EXECUTABLE", sys.executable).replace("$LIBSPEC_PATH", LIBSPEC_PATH).replace("$PORT", str(port))
        cmd = cmd.split(" ")

        env = os.environ.copy()
        env['WORKFLOW_ID'] = workflow.id()
        env['DIZEST_API'] = server.api()

        if cwd is not None:
            util.os.storage(cwd).makedirs()
            self.process = subprocess.Popen(cmd, shell=False, cwd=cwd, env=env)
        else:
            self.process = subprocess.Popen(cmd, shell=False, env=env)

        # wait for kernel server start
        counter = 0
        while True:
            if counter > 5:
                try:
                    self.kill()
                except Exception as e:
                    pass
                raise Exception("Kernel Error")
            try:
                requests.get(f"http://127.0.0.1:{port}/health", timeout=3)
                break
            except Exception as e:
                time.sleep(5)
                counter = counter + 1

        self.port = port
        self._uri = f"http://127.0.0.1:{port}"
        self.status = 'ready'

    def kernel_kill(self):
        self._kill()

    def kernel_stop(self):
        self._request()
        self.process.send_signal(signal.SIGABRT)

    def kernel_update(self):
        if self.workflow is None:
            return
        
        uri = self._uri
        port = self.port
        package = self.workflow.package
        data = dict()
        
        data['url'] = f"{uri}/update"
        data['data'] = dict()
        data['data']['package'] = json.dumps(package, default=util.string.json_default)
        self._send(data)

    def kernel_run(self, flow_id):
        if self.process is None:
            raise Exception("Spawner is not started")

        self.flow(flow_id).log.clear()

        uri = self._uri
        port = self.port
        workflow_id = self.workflow.id()

        data = dict()
        data['url'] = f"{uri}/run/{flow_id}"
        data['data'] = dict()

        self._send(data)

        self.workflow.server.send(id=workflow_id, flow_id=flow_id, mode='flow.status', data='pending')
        self.workflow.server.send(id=workflow_id, flow_id=flow_id, mode='flow.index', data='')

    # override abstract drive methods
    def drive_start(self):
        server = self.server

        kernelspec = self.kernelspec
        cwd = self.cwd

        port = random.randrange(10000, 60000)
        while util.os.port(port):
            port = random.randrange(10000, 60000)

        LIBSPEC_PATH = os.path.join(os.path.dirname(__file__), 'kernel')
        executable = server.config("executable")
        if executable is None:
            executable = sys.executable
        cmd = "$EXECUTABLE $LIBSPEC_PATH/drive.py $PORT".replace("$EXECUTABLE", executable).replace("$LIBSPEC_PATH", LIBSPEC_PATH).replace("$PORT", str(port))
        cmd = cmd.split(" ")

        env = os.environ.copy()

        if cwd is not None:
            util.os.storage(cwd).makedirs()
            self.process = subprocess.Popen(cmd, shell=False, cwd=cwd, env=env)
        else:
            self.process = subprocess.Popen(cmd, shell=False, env=env)

        # wait for kernel server start
        counter = 0
        while True:
            if counter > 5:
                try:
                    self.kill()
                except Exception as e:
                    pass
                raise Exception("Spawner Error")
            try:
                requests.get(f"http://127.0.0.1:{port}/health", timeout=3)
                break
            except Exception as e:
                time.sleep(5)
                counter = counter + 1

        self.port = port
        self._uri = f"http://127.0.0.1:{port}"
        self.status = 'ready'
    
    def drive_kill(self):
        self._kill()

    # override abstract terminal methods
    def terminal_start(self):
        server = self.server

        kernelspec = self.kernelspec
        cwd = self.cwd

        port = random.randrange(10000, 60000)
        while util.os.port(port):
            port = random.randrange(10000, 60000)

        LIBSPEC_PATH = os.path.join(os.path.dirname(__file__), 'kernel', 'spec')
        executable = server.config("executable")
        if executable is None:
            executable = sys.executable
        cmd = "$EXECUTABLE $LIBSPEC_PATH/python/terminal.py $PORT".replace("$EXECUTABLE", executable).replace("$LIBSPEC_PATH", LIBSPEC_PATH).replace("$PORT", str(port))
        cmd = cmd.split(" ")

        env = os.environ.copy()

        if cwd is not None:
            util.os.storage(cwd).makedirs()
            self.process = subprocess.Popen(cmd, shell=False, cwd=cwd, env=env)
        else:
            self.process = subprocess.Popen(cmd, shell=False, env=env)

        # wait for kernel server start
        counter = 0
        while True:
            if counter > 5:
                try:
                    self.kill()
                except Exception as e:
                    pass
                raise Exception("Spawner Error")
            try:
                requests.get(f"http://127.0.0.1:{port}/health", timeout=3)
                break
            except Exception as e:
                time.sleep(5)
                counter = counter + 1

        self.port = port
        self._uri = f"http://127.0.0.1:{port}"
        self.status = 'ready'
    
    def terminal_kill(self):
        self._kill()

class SudoSpawner(BaseSpawner):
    def __init__(self, server=None, workflow=None, kernelspec=None, cwd=None, mode="kernel"):
        super().__init__(server=server, workflow=workflow, kernelspec=kernelspec, cwd=cwd, mode=mode)
        self.name = 'linux'
        self.process = None
        self._uri = None
        self._request()
        self.cwd = cwd
        try:
            subprocess.run('useradd -m ' + self.user, shell=True, capture_output=True)
        except Exception as e:
            pass

    def _request(self):
        try:
            self.request.process.terminate()
        except Exception as e:
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
                            res = requests.post(url, data=data, timeout=None)
                            break
                        except Exception as e1:
                            time.sleep(5)
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

    def _kill(self):
        self._request()

        try:
            ppid = self.process.pid
            parent = psutil.Process(ppid)
            children = parent.children(recursive=True)
            for process in children:
                pid = process.pid
                os.system(f"kill -2 {pid}")
                time.sleep(5)
                os.system(f"kill -9 {pid}")
            
            os.system(f"kill -9 {ppid}")
        except Exception as e:
            pass

        self.process = None
        self.status = 'stop'
        self.port = None
        self._uri = None

    # override abstract kernel methods
    def uri(self):
        return self._uri
    
    def kernel_start(self):
        if self.process is not None:
            return 

        workflow = self.workflow
        server = workflow.server

        kernelspec = self.kernelspec
        cwd = self.cwd

        port = random.randrange(10000, 60000)
        while util.os.port(port):
            port = random.randrange(10000, 60000)

        LIBSPEC_PATH = os.path.join(os.path.dirname(__file__), 'kernel', 'spec')
        cmd = kernelspec['kernel'].replace("$EXECUTABLE", sys.executable).replace("$LIBSPEC_PATH", LIBSPEC_PATH).replace("$PORT", str(port))
        user = self.user
        WORKFLOW_ID = workflow.id()
        DIZEST_API = server.api()
        cmd = f"sudo -u {user} WORKFLOW_ID={WORKFLOW_ID} DIZEST_API={DIZEST_API} {cmd}"
        cmd = cmd.split(" ")

        if cwd is not None:
            if util.os.storage(cwd).exists() == False:
                util.os.storage(cwd).makedirs()
                subprocess.Popen(["chown", "-R", self.user + ":" + self.user, cwd], shell=False)
            self.process = subprocess.Popen(cmd, shell=False, cwd=cwd)
        else:
            self.process = subprocess.Popen(cmd, shell=False)

        # wait for kernel server start
        counter = 0
        while True:
            if counter > 5:
                try:
                    self.kill()
                except Exception as e:
                    pass
                raise Exception("Kernel Error")
            try:
                requests.get(f"http://127.0.0.1:{port}/health", timeout=3)
                break
            except Exception as e:
                time.sleep(5)
                counter = counter + 1

        self.port = port
        self._uri = f"http://127.0.0.1:{port}"
        self.status = 'ready'

    def kernel_kill(self):
        self._kill()

    def kernel_stop(self):
        self._request()
        try:
            parent = psutil.Process(self.process.pid)
            children = parent.children(recursive=True)
            for process in children:
                pid = process.pid
                os.system(f"kill -6 {pid}")
        except Exception as e:
            pass

    def kernel_update(self):
        if self.workflow is None:
            return
        
        uri = self._uri
        port = self.port
        package = self.workflow.package
        data = dict()
        
        data['url'] = f"{uri}/update"
        data['data'] = dict()
        data['data']['package'] = json.dumps(package, default=util.string.json_default)
        self._send(data)

    def kernel_run(self, flow_id):
        if self.process is None:
            raise Exception("Spawner is not started")

        self.flow(flow_id).log.clear()

        uri = self._uri
        port = self.port
        workflow_id = self.workflow.id()

        data = dict()
        data['url'] = f"{uri}/run/{flow_id}"
        data['data'] = dict()

        self._send(data)

        self.workflow.server.send(id=workflow_id, flow_id=flow_id, mode='flow.status', data='pending')
        self.workflow.server.send(id=workflow_id, flow_id=flow_id, mode='flow.index', data='')

    # override abstract drive methods
    def drive_start(self):
        server = self.server

        kernelspec = self.kernelspec
        cwd = self.cwd

        port = random.randrange(10000, 60000)
        while util.os.port(port):
            port = random.randrange(10000, 60000)

        LIBSPEC_PATH = os.path.join(os.path.dirname(__file__), 'kernel')
        cmd = "$EXECUTABLE $LIBSPEC_PATH/drive.py $PORT".replace("$EXECUTABLE", sys.executable).replace("$LIBSPEC_PATH", LIBSPEC_PATH).replace("$PORT", str(port))
        user = self.user
        cmd = f"sudo -u {user} {cmd}"
        cmd = cmd.split(" ")

        if cwd is not None:
            util.os.storage(cwd).makedirs()
            self.process = subprocess.Popen(cmd, shell=False, cwd=cwd)
        else:
            self.process = subprocess.Popen(cmd, shell=False)

        # wait for kernel server start
        counter = 0
        while True:
            if counter > 5:
                try:
                    self.kill()
                except Exception as e:
                    pass
                raise Exception("Spawner Error")
            try:
                requests.get(f"http://127.0.0.1:{port}/health", timeout=3)
                break
            except Exception as e:
                time.sleep(5)
                counter = counter + 1

        self.port = port
        self._uri = f"http://127.0.0.1:{port}"
        self.status = 'ready'
    
    def drive_kill(self):
        self._kill()

    # override abstract terminal methods
    def terminal_start(self):
        server = self.server

        kernelspec = self.kernelspec
        cwd = self.cwd

        port = random.randrange(10000, 60000)
        while util.os.port(port):
            port = random.randrange(10000, 60000)

        LIBSPEC_PATH = os.path.join(os.path.dirname(__file__), 'kernel')
        cmd = "$EXECUTABLE $LIBSPEC_PATH/terminal.py $PORT".replace("$EXECUTABLE", sys.executable).replace("$LIBSPEC_PATH", LIBSPEC_PATH).replace("$PORT", str(port))
        cmd = cmd.split(" ")

        user = self.user
        cmd = f"sudo -u {user} {cmd}"

        env = os.environ.copy()

        if cwd is not None:
            util.os.storage(cwd).makedirs()
            self.process = subprocess.Popen(cmd, shell=False, cwd=cwd, env=env)
        else:
            self.process = subprocess.Popen(cmd, shell=False, env=env)

        # wait for kernel server start
        counter = 0
        while True:
            if counter > 5:
                try:
                    self.kill()
                except Exception as e:
                    pass
                raise Exception("Spawner Error")
            try:
                requests.get(f"http://127.0.0.1:{port}/health", timeout=3)
                break
            except Exception as e:
                time.sleep(5)
                counter = counter + 1

        self.port = port
        self._uri = f"http://127.0.0.1:{port}"
        self.status = 'ready'
    
    def terminal_kill(self):
        self._kill()