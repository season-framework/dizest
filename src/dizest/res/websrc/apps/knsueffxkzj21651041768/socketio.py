import os
import season
import time
import urllib
import requests
import traceback
import datetime

Dizest = wiz.model("dizest/scheduler")

class Controller:
    def __init__(self, wiz):
        pass

    def join(self, wiz, data):
        self.fid = fid = data['id']
        wiz.flask_socketio.join_room(fid, namespace=wiz.socket.namespace)
        dizest = Dizest.test(fid)
        wiz.socket.emit("status", dict(dizest.status(fid)), to=fid, broadcast=True)

    def leave(self, wiz, data):
        fid = data['id']
        wiz.flask_socketio.leave_room(fid, namespace=wiz.socket.namespace)

    def connect(self, wiz, data):
        pass

    def disconnect(self, wiz, data):
        pass