import season
import datetime
import json
import os

class Controller(wiz.controller("base")):
    def __startup__(self, wiz):
        super().__startup__(wiz)

        status = wiz.model("dizest/config").status()
        if status == False: wiz.response.redirect("/")
        versioncheck = wiz.model("dizest/config").version()
