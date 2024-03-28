import season
import datetime
import json
import os

class Controller(wiz.controller("portal/season/base")):
    def __init__(self):
        super().__init__()
        if wiz.session.has("id") == False:
            wiz.response.status(401, "Access Denied")
