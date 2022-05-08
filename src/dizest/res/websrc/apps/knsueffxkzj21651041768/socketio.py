import os
import season
import time
import builtins
import urllib
import requests
import traceback
import datetime

def logger_fn(host, fid):
    def logger(*args, color=94):
        tag = f"[dizest][{fid}]"
        log_color = color
        args = list(args)
        for i in range(len(args)): 
            args[i] = str(args[i])
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        logdata = f"\033[{log_color}m[{timestamp}]{tag}\033[0m " + " ".join(args)
        res = requests.post(host, {"data": logdata, "id": fid})
    return logger

class Controller:
    def __init__(self, wiz):
        host = urllib.parse.urlparse(wiz.flask.request.base_url)
        self.host = f"{host.scheme}://{host.netloc}/dizest/api/kernel/dev"

    def join(self, wiz, data):
        self.fid = fid = data['id']
        wiz.flask_socketio.join_room(fid, namespace=wiz.socket.namespace)
        Dizest = wiz.model("dizest/scheduler")
        dizest = Dizest.test(fid, logger=logger_fn(self.host, fid))
        wiz.socket.emit("status", dizest.status(fid), to=fid, broadcast=True)

    def leave(self, wiz, data):
        fid = data['id']
        wiz.flask_socketio.leave_room(fid, namespace=wiz.socket.namespace)

    def connect(self, wiz, data):
        pass

    def disconnect(self, wiz, data):
        pass

    def run(self, wiz, data):
        try:
            fid = data['id']
            Dizest = wiz.model("dizest/scheduler")
            dizest = Dizest.test(fid, logger=logger_fn(self.host, fid))
            if dizest.status(fid)['status'] in ['running', 'pending']:
                return
            dizest.run(fid)
        except Exception as e:
            pass

    def stop(self, wiz, data):
        try:
            fid = data['id']
            Dizest = wiz.model("dizest/scheduler")
            dizest = Dizest.test(fid, logger=logger_fn(self.host, fid))
            dizest.stop()
            wiz.socket.emit("status", dizest.status(fid), to=fid, broadcast=True)
        except Exception as e:
            pass