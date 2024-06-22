from flask import Response
import os
import season
import sass
import requests

Kernel = wiz.model("portal/dizest/kernel")
config = wiz.model("portal/dizest/config")

segment = wiz.request.match("/api/dizest/ui/<zone>/<spawner_id>/<flow_id>/<path:path>")
if segment is None:
    wiz.response.status(404)

action = segment.path
zone = segment.zone
spawner_id = segment.spawner_id
flow_id = segment.flow_id

if config.acl(wiz, zone) == False:
    wiz.response.status(401)

kernel = Kernel(zone)
workflow = kernel.workflow_by_spawner(spawner_id)

if workflow is None:
    wiz.response.status(404)

basepath = workflow.spawner.get("cwd")
fs = season.util.fs(os.path.join(basepath))

wfdata = workflow.data()
if wfdata is None:
    wiz.response.abort(404)

app_id = wfdata['flow'][flow_id]['app_id']
app = wfdata['apps'][app_id]

def app_get(key, default=None):
    try:
        if app[key] is not None:
            return app[key]
    except:
        pass
    return default

if action in ['render']:
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
    text = '''
    window.dizest = (()=> {
        let Style = {
            base: [
                "color: #fff",
                "background-color: #444",
                "padding: 2px 4px",
                "border-radius: 2px"
            ],
            warning: [
                "color: #eee",
                "background-color: red"
            ],
            success: [
                "background-color: green"
            ]
        };

        let obj = {};

        obj.log = function() {
            let style = Style.base.join(';') + ';';
            style += Style.base.join(';');
            console.log(`%cdizest.js`, style, ...arguments);
        }

        obj.url = (fnname)=> "{url}/" + fnname;

        obj.async = obj.function = obj.call = async(fnname, data, opts = {})=> {
            let _url = obj.url(fnname);
            
            let ajax = {
                url: _url,
                type: "POST",
                data: data,
                ...opts
            };

            return new Promise((resolve) => {
                $.ajax(ajax).always(function (a, b, c) {
                    resolve(a, b, c);
                });
            });
        };
        return obj;
    })();
    '''

    url = f'/api/dizest/ui/{zone}/{spawner_id}/{flow_id}/api'
    text = wiz.project.fs("src/assets").read("jquery.js") + text
    text = text.replace('{url}', url)

    wiz.response.send(text, content_type="text/javascript")

if action.startswith('assets'):
    segment = wiz.request.match("/api/dizest/ui/<zone>/<spawner_id>/<flow_id>/assets/<path:path>")
    path = segment.path
    path = fs.abspath(path)
    wiz.response.download(path)

if action.startswith('api'):
    segment = wiz.request.match("/api/dizest/ui/<zone>/<spawner_id>/<flow_id>/api/<path:path>")
    fnname = segment.path

    spawner_uri = workflow.spawner.uri()
    request = wiz.request.request()
    
    kwargs = dict(
        method=request.method,
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.values,
        cookies=request.cookies,
        files=request.files)
    
    kwargs["url"] = spawner_uri + "/flow/api/" + spawner_id + "/" + flow_id + "/" + fnname
    kwargs["allow_redirects"] = False

    resp = requests.request(**kwargs)
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
    response = Response(resp.content, resp.status_code, headers)

    wiz.response.response(response)

wiz.response.status(404)