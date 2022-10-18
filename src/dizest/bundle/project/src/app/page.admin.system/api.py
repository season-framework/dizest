import sys
import os
import season
import string
import json
import time
import psutil
import signal
import subprocess
import requests
import dizest

if wiz.session.get("role") != "admin":
    wiz.response.abort(401)

fs = wiz.workspace("service").fs("config")

def load():
    process = psutil.Process(os.getpid())
    deploy = season.util.std.stdClass()
    deploy.process_id = os.getpid()
    deploy.subprocess = len(psutil.Process(os.getpid()).children(recursive=True))
    deploy.cwd = os.getcwd()
    deploy.dizest_version = dizest.version
    deploy.dizest_ui_version = wiz.model("dizest").VERSION
    config = fs.read.json("config.json", {})
    wiz.response.status(200, deploy=deploy, config=config)

def update():
    data = wiz.request.query("data", True)
    data = json.loads(data)
    config = fs.write.json("config.json", data)
    wiz.response.status(200)

def restart():    
    pid = os.getpid()
    for child in psutil.Process(pid).children(recursive=True):
        child.terminate()
        os.kill(child.pid, signal.SIGKILL)
    os.kill(pid, signal.SIGKILL)
    wiz.response.status(200)