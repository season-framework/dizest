import json

dconfig = wiz.model("portal/dizest/dconfig")
fs = dconfig.configfs()

def load():
    config = fs.read.json("config.json", {})
    wiz.response.status(200, config=config)

def update():
    data = wiz.request.query("data", True)
    data = json.loads(data)
    config = fs.write.json("config.json", data)
    wiz.response.status(200)