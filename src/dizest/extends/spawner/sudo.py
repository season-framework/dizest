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
        'cwd': (None, None),
        'socket_uri': (None, None),
        'socket_namespace': (None, None),
        'user': (None, None),
        'executable': (None, sys.executable)
    }

class SudoSpawner(BaseSpawner):
    NAMESPACE = "sudo"
    CONFIGCLASS = Config
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if self.config.user is None: raise Exception("`user` not defined")
        if self.config.cwd is None: raise Exception("`cwd` not defined")
        if self.config.socket_uri is None: raise Exception("`socket_uri` not defined")
        if self.config.socket_namespace is None: raise Exception("`socket_namespace` not defined")
        
        self.process = None

        try:
            subprocess.run('useradd -m ' + self.config.user, capture_output=True, shell=True)
        except Exception as e:
            pass
        
    def start(self):
        if self.process is not None:
            return False

        user = self.config.user
        cwd = self.config.cwd
        socket_uri = self.config.socket_uri
        socket_namespace = self.config.socket_namespace
        executable = self.config.executable

        port = random.randrange(10000, 60000)
        while util.os.port(port):
            port = random.randrange(10000, 60000)

        if util.os.storage(cwd).exists() == False:
            util.os.storage(cwd).makedirs()
            subprocess.Popen(["chown", "-R", user + ":" + user, cwd], **SUBPROCESS_ARGS)
        
        LIBSPEC_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'api', 'runner.py')

        cmd = f"{executable} {LIBSPEC_PATH}"
        cmd = f"sudo -u {user} SOCKET_URI={socket_uri} SOCKET_NAMESPACE={socket_namespace} PORT={port} ID={port} {cmd}"
        cmd = cmd.split(" ")

        uri = f"http://127.0.0.1:{port}".strip()

        self.process = subprocess.Popen(cmd, cwd=cwd, **SUBPROCESS_ARGS)

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
        return uri

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
        return True
    
    def port(self):
        return self.config.port

    def uri(self):
        return self.config.uri

    def status(self):
        return self.config.status