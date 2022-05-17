import os
import season
import time
import builtins
import urllib
import requests
import traceback
import datetime

def logger_fn(host, workflow_id):
    def logger(*args, color=94):
        tag = f"[dizest]"
        log_color = color
        args = list(args)
        for i in range(len(args)): 
            args[i] = str(args[i])
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        logdata = f"\033[{log_color}m[{timestamp}]{tag}\033[0m " + " ".join(args)
        res = requests.post(host, {"data": logdata, "id": workflow_id})
    return logger

Dizest = wiz.model("dizest/scheduler")
db = wiz.model("dizest/db").use("workflow")

class Controller:
    def __init__(self, wiz):
        host = urllib.parse.urlparse(wiz.flask.request.base_url)
        self.host = f"{host.scheme}://{host.netloc}/dizest/api/kernel/workflow"
        
    def join(self, wiz, data):
        try:
            wiz.flask_socketio.join_room(data, namespace=wiz.socket.namespace)
            wiz.socket.emit("join", data, to=data, broadcast=True)
        except:
            pass

    def stop(self, wiz, data):
        try:
            wpid = data['workflow_id']
            fid = data['flow_id'] if 'flow_id' in data else None
            dizest = Dizest(wpid, logger=logger_fn(self.host, wpid))
            dizest.stop(fid)
            if fid is None:
                wiz.socket.emit("stop", fid, to=wpid, broadcast=True)
            else:
                wiz.socket.emit("status", dizest.status(fid), to=wpid, broadcast=True)
        except:
            pass

    def status(self, wiz, data):
        try:
            wpid = data['workflow_id']
            fid = data['flow_id'] if 'flow_id' in data else None
            dizest = Dizest(wpid, logger=logger_fn(self.host, wpid))
            if dizest is None:
                return
            wiz.socket.emit("status", dizest.status(fid), to=wpid, broadcast=True)
        except:
            pass
        
    def run(self, wiz, data):
        try:
            wpid = data['workflow_id']
            fids = data['flow_id'] if 'flow_id' in data else None
            if fids is None: return
            
            workflow = db.get(id=wpid)
            dizest = Dizest(wpid, package=workflow, logger=logger_fn(self.host, wpid))
            
            fids = fids.split(",")
            for fid in fids:
                status = dizest.status(fid)
                if status['status'] == 'pending' or status['status'] == 'running':
                    continue
                dizest.run(fid)
        except:
            pass

    def connect(self, wiz, data):
        pass

    def disconnect(self, wiz, data):            
        pass
