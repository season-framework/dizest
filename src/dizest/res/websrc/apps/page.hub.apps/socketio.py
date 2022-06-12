import os
import season
import time
import urllib
import requests
import traceback
import datetime

Dizest = wiz.model("dizest/scheduler")

class Controller:
    def __init__(self):
        pass

    def join(self, wiz, data, io):
        self.fid = fid = data['id']
        io.join(fid)
        dizest = Dizest.test(fid)
        io.emit("status", dict(dizest.status(fid)), to=fid, broadcast=True)

    def leave(self, wiz, data, io):
        fid = data['id']
        io.leave(fid)

    def connect(self, wiz, data):
        pass

    def disconnect(self, wiz, data):
        pass