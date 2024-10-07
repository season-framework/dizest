from flask import Response
import os
import season
import sass
import requests

struct = wiz.model("portal/dizest/struct")
config = struct.config

segment = wiz.request.match("/ui/<kernel_id>/<flow_id>/<path:path>")
if segment is None:
    wiz.response.status(400)

kernel_id = segment.kernel_id
flow_id = segment.flow_id
action = segment.path

if kernel_id is None:
    wiz.response.status(400, "kernel_id not defined")
if flow_id is None:
    wiz.response.status(400, "flow_id not defined")

kernel = struct.kernel.get(kernel_id)
if kernel is None:
    wiz.response.status(401)

basepath = kernel.spawner.config.cwd
fs = season.util.fs(os.path.join(basepath))

# find app data
wfdata = kernel.workflow.data
if wfdata is None:
    wiz.response.status(404, 'workflow not initialized')
if flow_id not in wfdata['flow']:
    wiz.response.status(404, 'not exists flow')
app_id = wfdata['flow'][flow_id]['app_id']
if app_id not in wfdata['apps']:
    wiz.response.status(404, 'not exists app')
app = wfdata['apps'][app_id]

def app_get(key, default=None):
    try:
        if app[key] is not None:
            return app[key]
    except:
        pass
    return default

if action == 'render':
    text = app_get("html", "")
    wiz.response.send(text, content_type="text/html")

if action == 'render/view.js':
    text = app_get("js", "")
    wiz.response.send(text, content_type="text/javascript")

if action == 'render/view.css':
    text = app_get("css", "")
    try:
        text = sass.compile(string=text)
        text = str(text)
    except Exception as e:
        text = ""
    wiz.response.send(text, content_type="text/css")

if action == 'dizest.js':
    assetsfs = wiz.project.fs("bundle/src/assets/portal/dizest")
    text = assetsfs.read("dizest.js")
    url = f'/ui/{kernel_id}/{flow_id}/api'
    text = text.replace('{url}', url)
    text = assetsfs.read("jquery.js") + text
    wiz.response.send(text, content_type="text/javascript")

if action.startswith('assets'):
    segment = wiz.request.match("/ui/<kernel_id>/<flow_id>/assets/<path:path>")
    path = segment.path
    path = fs.abspath(path)
    wiz.response.download(path)

if action.startswith('api'):
    segment = wiz.request.match("/ui/<kernel_id>/<flow_id>/api/<path:path>")
    fnname = segment.path

    spawner_uri = kernel.spawner.uri()
    request = wiz.request.request()
    
    kwargs = dict(
        method=request.method,
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.values,
        cookies=request.cookies,
        files=request.files)
    
    kwargs["url"] = spawner_uri + "/flow/api/" + flow_id + "/" + fnname
    kwargs["allow_redirects"] = False

    resp = requests.request(**kwargs)
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
    response = Response(resp.content, resp.status_code, headers)

    wiz.response.response(response)

wiz.response.status(404)