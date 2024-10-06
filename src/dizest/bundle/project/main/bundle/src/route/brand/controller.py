import os
import season
import base64
from io import BytesIO
from PIL import Image 

struct = wiz.model("portal/dizest/struct")
config = struct.config

segment = wiz.request.match("/brand/<action>/<path:path>")
action = segment.action
fs = wiz.fs()

if action == "logo":
    config = fs.read.json("dizest.json", {})
    if 'logo' in config and len(config['logo']) > 0:
        img = config['logo'].split(",")[1]
        buf = BytesIO(base64.b64decode(img))
        img = Image.open(buf)
        img = img.convert('RGBA')
        wiz.response.PIL(img, type="PNG")
    
    fs = wiz.project.fs("bundle", "src", "assets", "brand")
    wiz.response.download(fs.abspath("logo.png"), as_attachment=False)

if action == "icon":
    fs = config.fs
    config = fs.read.json("dizest.json", {})
    if 'icon' in config and len(config['icon']) > 0:
        img = config['icon'].split(",")[1]
        buf = BytesIO(base64.b64decode(img))
        img = Image.open(buf)
        img = img.convert('RGBA')
        wiz.response.PIL(img, type="PNG")
    
    fs = wiz.project.fs("bundle", "src", "assets", "brand")
    wiz.response.download(fs.abspath("icon.ico"), as_attachment=False)

wiz.response.abort(404)