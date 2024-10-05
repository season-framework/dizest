from dizest.base.spawner import BaseSpawner
from dizest.base.config import BaseConfig
from dizest import util
import sys
import os
import subprocess
import random
import requests
import time
import psutil

SUBPROCESS_ARGS = dict(
    shell=False,
    stdin=subprocess.DEVNULL,
    stdout=subprocess.DEVNULL, 
    stderr=subprocess.DEVNULL
)

class Config(BaseConfig):
    DEFAULT_VALUES = {
        'id': (None, None),
        'cwd': (None, None),
        'socket_uri': (None, None),
        'socket_namespace': (None, None),
        'executable': (None, sys.executable)
    }

class SimpleSpawner(BaseSpawner):
    NAMESPACE = "simple"
    CONFIGCLASS = Config
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if self.config.id is None: raise Exception("`id` not defined")
        if self.config.cwd is None: raise Exception("`cwd` not defined")
        if self.config.socket_uri is None: raise Exception("`socket_uri` not defined")
        if self.config.socket_namespace is None: raise Exception("`socket_namespace` not defined")
        
        self.process = None
        
    def start(self):
        if self.process is not None:
            return False

        id = self.config.id
        cwd = self.config.cwd
        socket_uri = self.config.socket_uri
        socket_namespace = self.config.socket_namespace
        executable = self.config.executable

        port = random.randrange(10000, 60000)
        while util.os.port(port):
            port = random.randrange(10000, 60000)

        if util.os.storage(cwd).exists() == False:
            util.os.storage(cwd).makedirs()

        LIBSPEC_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'api', 'runner.py')

        env = dict()
        env['SOCKET_URI'] = socket_uri
        env['SOCKET_NAMESPACE'] = socket_namespace
        env['PORT'] = str(port)
        env['ID'] = id
        cmd = f"{executable} {LIBSPEC_PATH}"
        cmd = cmd.split(" ")

        uri = f"http://127.0.0.1:{port}".strip()

        self.process = subprocess.Popen(cmd, cwd=cwd, env=env, **SUBPROCESS_ARGS)

        counter = 0
        while True:
            if counter > 20:
                try:
                    self.stop()
                except Exception as e:
                    pass
                raise Exception("Kernel Error")
            try:
                requests.get(f"{uri}/health", timeout=3)
                break
            except Exception as e:
                time.sleep(1)
                counter = counter + 1

        self.config.pid = self.process.pid
        self.config.port = port
        self.config.uri = uri
        self.config.status = 'start'
        return self

    def stop(self):        
        try:
            ppid = self.config.pid
            parent = psutil.Process(ppid)
            children = parent.children(recursive=True)
            for process in children:
                pid = process.pid
                os.system(f"kill -9 {pid} > /dev/null")
            os.system(f"kill -9 {ppid} > /dev/null")
        except Exception as e:
            return False
        
        uri = self.uri()
        counter = 0
        
        while True:
            if counter > 20:
                raise Exception("Kernel Error")
            try:
                requests.get(f"{uri}/health", timeout=3)
                counter = counter + 1
            except Exception as e:
                break
            time.sleep(1)

        self.process = None
        self.config.pid = None
        self.config.port = None
        self.config.uri = None
        self.config.status = 'stop'
        return self
    
    def port(self):
        return self.config.port

    def uri(self):
        return self.config.uri

    def status(self):
        return self.config.status