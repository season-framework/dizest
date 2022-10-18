import json

if wiz.session.get("role") != "admin":
    wiz.response.abort(401)

fs = wiz.workspace("service").fs("config")

def load():
    config = fs.read.json("database.json", dict(type='sqlite', path="dizest.db"))
    wiz.response.status(200, config)

def update():
    data = wiz.request.query("data", True)
    data = json.loads(data)
    config = fs.write.json("database.json", data)
    wiz.response.status(200)