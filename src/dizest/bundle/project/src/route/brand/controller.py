import os
import season
import base64
from io import BytesIO
from PIL import Image 

segment = wiz.request.match("/brand/<action>/<path:path>")

action = segment.action

if action == "logo":
    fs = wiz.workspace("service").fs("config")
    config = fs.read.json("config.json", {})
    if 'logo' in config and len(config['logo']) > 0:
        img = config['logo'].split(",")[1]
        buf = BytesIO(base64.b64decode(img))
        img = Image.open(buf)
        img = img.convert('RGBA')
        wiz.response.PIL(img, type="PNG")
    
    fs = wiz.workspace("service").fs("src", "assets", "images", "brand")
    wiz.response.download(fs.abspath("dizest-hub-white.png"), as_attachment=False)

if action == "icon":
    fs = wiz.workspace("service").fs("config")
    config = fs.read.json("config.json", {})
    if 'icon' in config and len(config['icon']) > 0:
        img = config['icon'].split(",")[1]
        buf = BytesIO(base64.b64decode(img))
        img = Image.open(buf)
        img = img.convert('RGBA')
        wiz.response.PIL(img, type="PNG")
    
    fs = wiz.workspace("service").fs("src", "assets", "images", "brand")
    wiz.response.download(fs.abspath("icon.ico"), as_attachment=False)

wiz.response.abort(404)