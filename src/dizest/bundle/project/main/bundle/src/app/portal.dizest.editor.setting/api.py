import os
import psutil
import signal
import json
import sys
import pkg_resources
import subprocess
import dizest

struct = wiz.model("portal/dizest/struct")
config = struct.config
config.acl()

def restart():
    pid = os.getpid()
    for child in psutil.Process(pid).children(recursive=True):
        child.terminate()
        os.kill(child.pid, signal.SIGKILL)
    os.kill(pid, signal.SIGKILL)
    wiz.response.status(200)

def status():
    wiz.response.status(200)

def verify():
    path = wiz.request.query("path", True)
    python_version = os.popen(path + " --version").read()
    python_version = python_version.replace("\n", " ").strip()    
    wiz.response.status(200, len(python_version) > 0)
