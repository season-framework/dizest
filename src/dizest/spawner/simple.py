from dizest.spawner.base import BaseSpawner
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

SUBPROCESS_ARGS = dict(
    shell=False,
    stdin=subprocess.DEVNULL,
    stdout=subprocess.DEVNULL, 
    stderr=subprocess.DEVNULL
)

class SimpleSpawner(BaseSpawner):
    def __init__(self, kernelspec=None, cwd=None, user=None, dSocket=None):
        self.name = "simple"
        if user is None: raise Exception("`user` not defined")
        if cwd is None: raise Exception("`cwd` not defined")
        if kernelspec is None: raise Exception("`kernelspec` not defined")
        if dSocket is None: raise Exception("`dSocket` not defined")
        super().__init__(kernelspec=kernelspec, cwd=cwd, user=user, dSocket=dSocket, uri=None, port=None)
        
        self.process = None

        try:
            subprocess.run('useradd -m ' + user, capture_output=True, shell=True)
        except Exception as e:
            pass
        
    def start(self):
        kernelspec = self.getMeta("kernelspec", dict(name='base'))
        user = self.getMeta("user")
        if user is None: raise Exception("`user` not defined")
        cwd = self.getMeta("cwd", os.path.join("/home", user))
        dSocket = self.getMeta("dSocket")

        port = random.randrange(10000, 60000)
        while util.os.port(port):
            port = random.randrange(10000, 60000)

        if util.os.storage(cwd).exists() == False:
            util.os.storage(cwd).makedirs()
            subprocess.Popen(["chown", "-R", user + ":" + user, cwd], **SUBPROCESS_ARGS)
        
        if 'executable' in kernelspec: executable = kernelspec['executable']
        else: executable = sys.executable

        LIBSPEC_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'daemon', 'simple.py')
        cmd = f"{executable} {LIBSPEC_PATH}"
        cmd = f"sudo -u {user} DSOCKET={dSocket} PORT={port} {cmd}"
        cmd = cmd.split(" ")

        uri = f"http://127.0.0.1:{port}".strip()
        
        self.process = subprocess.Popen(cmd, cwd=cwd, **SUBPROCESS_ARGS)

        counter = 0
        while True:
            if counter > 60:
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

        self.setMeta(port=port, uri=uri, status='ready')
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

            self.process = None
            self.setMeta(uri=None, port=None, status='stop')
            return True
        except Exception as e:
            pass
        return False

    def uri(self):
        return self.getMeta("uri")