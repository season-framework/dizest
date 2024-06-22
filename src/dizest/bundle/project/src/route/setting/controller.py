import json
config = wiz.model("portal/dizest/config")
fs = config.fs
config = fs.read.json(".dizest/config.json", {})
wiz.response.status(200, config)
