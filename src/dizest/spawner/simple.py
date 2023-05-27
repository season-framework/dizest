from dizest.spawner.base import BaseSpawner
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

class SimpleSpawner(BaseSpawner):
    def __init__(self, spec=None, cwd=None, user=None, socket=None):
        self.name = "simple"
        if user is None: raise Exception("`user` not defined")
        if cwd is None: raise Exception("`cwd` not defined")
        if spec is None: raise Exception("`spec` not defined")
        if socket is None: raise Exception("`socket` not defined")
        super().__init__(spec=spec, cwd=cwd, user=user, socket=socket, uri=None, port=None)
        
        self.process = None

        try:
            subprocess.run('useradd -m ' + user, capture_output=True, shell=True)
        except Exception as e:
            pass
        
    def start(self):
        if self.process is not None:
            return False

        spec = self.get("spec", dict(name='base'))
        user = self.get("user")
        if user is None: raise Exception("`user` not defined")
        cwd = self.get("cwd", os.path.join("/home", user))
        socket = self.get("socket")

        port = random.randrange(10000, 60000)
        while util.os.port(port):
            port = random.randrange(10000, 60000)

        if util.os.storage(cwd).exists() == False:
            util.os.storage(cwd).makedirs()
            subprocess.Popen(["chown", "-R", user + ":" + user, cwd], **SUBPROCESS_ARGS)
        
        if 'executable' in spec: executable = spec['executable']
        else: executable = sys.executable

        LIBSPEC_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'daemon', 'simple.py')
        cmd = f"{executable} {LIBSPEC_PATH}"
        cmd = f"sudo -u {user} SOCKET={socket} PORT={port} {cmd}"
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

        self.set(port=port, uri=uri, status='start')
        return uri

    def stop(self):        
        try:
            ppid = self.process.pid
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
        self.set(uri=None, port=None, status='stop')
        return True

    def uri(self):
        return self.get("uri")

    def status(self):
        return self.get('status', 'stop')