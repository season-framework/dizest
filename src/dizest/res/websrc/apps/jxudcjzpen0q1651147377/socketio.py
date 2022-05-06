import os
import datetime
import time

Dizest = wiz.model("dizest/scheduler")
db = wiz.model("dizest/db").use("workflow")

class Controller:
    def __init__(self, wiz):
        self.cache = wiz.cache
        
    def join(self, wiz, data):
        wiz.flask_socketio.join_room(data, namespace=wiz.socket.namespace)
        wiz.socket.emit("join", data, to=data, broadcast=True)

    def stop(self, wiz, data):
        wpid = data['workflow_id']
        fid = data['flow_id'] if 'flow_id' in data else None
        dizest = Dizest(wpid)
        dizest.stop(fid)
        if fid is None:
            wiz.socket.emit("stop", fid, to=wpid, broadcast=True)
        else:
            wiz.socket.emit("status", dizest.status(fid), to=wpid, broadcast=True)

    def status(self, wiz, data):
        wpid = data['workflow_id']
        fid = data['flow_id'] if 'flow_id' in data else None
        dizest = Dizest(wpid)
        if dizest is None:
            return
        wiz.socket.emit("status", dizest.status(fid), to=wpid, broadcast=True)
        
    def run(self, wiz, data):
        wpid = data['workflow_id']
        fids = data['flow_id'] if 'flow_id' in data else None
        if fids is None: return
        
        workflow = db.get(id=wpid)
        dizest = Dizest(wpid, workflow)
        
        fids = fids.split(",")
        for fid in fids:
            status = dizest.status(fid)
            if status['status'] == 'pending' or status['status'] == 'running':
                continue
            dizest.run(fid)

    def connect(self, wiz, data):
        pass

    def disconnect(self, wiz, data):            
        pass
