import os
import json

struct = wiz.model("portal/dizest/struct")
config = struct.config
config.acl()
fs = wiz.fs()

segment = wiz.request.match("/api/dizest/config/<path:path>")
action = segment.path

if action == 'load':
    data = fs.read.json("dizest.json", {})
    keys = ['use_ai', 'llm_gateway', 'llm_model']
    for key in keys:
        if key not in data or data[key] == '' or data[key] is None:
            data[key] = config[key]
    wiz.response.status(200, data)

if action == 'update':
    data = wiz.request.query("data", True)
    data = json.loads(data)
    fs.write.json("dizest.json", data)
    wiz.response.status(200)
