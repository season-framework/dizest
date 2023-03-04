import season
import datetime
import json
import os

class Controller(wiz.controller("base")):
    def __init__(self):
        super().__init__()
        
        if wiz.session.get("role") != 'admin':
            wiz.response.status(401)
