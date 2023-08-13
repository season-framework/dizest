import json

config = wiz.model("portal/dizest/config")

zone = wiz.request.query("zone", True)

if config.admin_access(wiz, zone) == False:
    wiz.response.status(401)

fs = config.fs

def load():
    config = fs.read.json(".dizest/config.json", {})
    wiz.response.status(200, config)

def update():
    data = wiz.request.query("data", True)
    data = json.loads(data)
    if fs.exists(".dizest") == False:
        fs.makedirs(".dizest")
    fs.write.json(".dizest/config.json", data)
    wiz.response.status(200)