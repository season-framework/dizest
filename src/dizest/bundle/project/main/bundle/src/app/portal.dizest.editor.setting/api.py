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

def check():
    executable_path = wiz.request.query("executable_path", True)
    try:
        output = subprocess.check_output(f"{executable_path} -m pip list | grep dizest", shell=True, stderr=subprocess.DEVNULL)
        output = output.decode()
        code = 400
        if 'dizest' in output and dizest.version in output:
            code = 200
        output = output.strip().replace("dizest", "").strip()
    except:
        code = 400
        output = "none"
    wiz.response.status(code, output)

def upgrade():
    executable_path = wiz.request.query("executable_path", True)
    output = subprocess.check_output(f"{executable_path} -m pip install -U dizest", shell=True, stderr=subprocess.DEVNULL)
    check()