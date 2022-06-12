import os
import season
import time
import builtins
import urllib
import requests
import traceback
import datetime

Dizest = wiz.model("dizest/scheduler")
db = wiz.model("dizest/db").use("workflow")

class Controller:
    def __init__(self):
        pass
        
    def join(self, wiz, data, io):
        try:
            io.join(data)
            io.emit("join", data, to=data, broadcast=True)
        except:
            pass

    def status(self, wiz, data, io):
        try:
            wpid = data['workflow_id']
            fid = data['flow_id'] if 'flow_id' in data else None
            dizest = Dizest(wpid)
            if dizest is None:
                return
            io.emit("status", dict(dizest.status(fid)), to=wpid, broadcast=True)
        except:
            pass

    def connect(self, wiz, data):
        pass

    def disconnect(self, wiz, data):            
        pass
