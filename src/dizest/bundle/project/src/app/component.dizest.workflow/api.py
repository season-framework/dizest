import os
import season
import json
import datetime
from flask import Response
from crontab import CronTab
import urllib
import pypugjs
from pypugjs.ext import jinja
import sass

if wiz.request.uri().split("/")[4] not in ['drive_api', 'render', 'api']:
    workflow_id = wiz.request.query("workflow_id", True)
    namespace = wiz.request.query("namespace", True)
    user = wiz.session.get("id")
    server_id = namespace + "-" + user

    db = wiz.model("orm").use(namespace)
    server = wiz.model("dizest").load(server_id).server(user=user)
    workflow = server.workflow_by_id(workflow_id)

def kernel():
    data = server.kernelspecs()
    rows = []
    for item in data:
        item = server.kernelspec(item)
        rows.append(item)
    wiz.response.status(200, rows)

def get():
    data = db.get(id=workflow_id, user=user)
    if workflow is not None:
        data['status'] = workflow.status()
        data['kernel'] = workflow.kernelspec()
    else:
        data['status'] = 'stop'
        data['kernel'] = server.kernelspecs()[0]
    wiz.response.status(200, data)

def update():
    try:
        data = wiz.request.query("data", True)
        data = json.loads(data)
        if 'created' not in data:
            data['created'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['updated'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            del data['language']
        except:
            pass
        workflow.update(data)
        db.update(data, id=workflow_id)
    except Exception as e:
        wiz.response.status(500, str(e))
    wiz.response.status(200)

def start():
    specs = server.kernelspecs()
    spec = wiz.request.query("spec", None)
    if spec not in specs:
        wiz.response.status(500, f'not supported kernel spec')
    
    workflow = server.workflow_by_id(workflow_id)    
    if workflow is None:
        wpdata = db.get(id=workflow_id, user=user)
        workflow = server.workflow(wpdata)

    workflow.spawn(kernel_name=spec)
    wiz.response.status(200)

def kill():
    try:
        workflow.kill()
    except:
        pass
    wiz.response.status(200)

def run():
    try:
        fids = wiz.request.query("flow", None)
        if fids is None:
            workflow.run()
        else:
            fids = fids.split(",")
            for fid in fids:
                flow = workflow.flow(fid)
                flow.run()
    except Exception as e:
        wiz.response.status(500, str(e))
    wiz.response.status(200)

def stop():
    try:
        workflow.stop()
    except:
        pass
    wiz.response.status(200)

def kill():
    try:
        workflow.kill()
    except:
        pass
    wiz.response.status(200)

def status():
    log = wiz.request.query("log", False)
    if log == 'true': log = True
    else: log = False

    status = dict()
    try:
        flows = workflow.flows()
        for flow_id in flows:
            try:
                flow = workflow.flow(flow_id)
            except:
                pass            
            try:
                status[flow_id] = dict()
                status[flow_id]['flow_id'] = flow_id
                status[flow_id]['status'] = flow.status()
                status[flow_id]['index'] = flow.index()
            except:
                pass

            if log:
                try:
                    logs = flow.log()
                    status[flow_id]['log'] = "".join(logs)
                except:
                    pass
    except Exception as e:
        pass

    wiz.response.status(200, status)


# Drive API
def drive_api(segment):
    segment = segment.path.split("/")

    namespace = segment[0]
    workflow_id = segment[1]
    user = wiz.session.get("id")
    server_id = namespace + "-" + user

    db = wiz.model("orm").use(namespace)
    server = wiz.model("dizest").load(server_id).server(user=user)
    workflow = server.workflow_by_id(workflow_id)

    fnname = segment[2]
    path = "/".join(segment[3:])
    
    request = wiz.request.request()
    resp = None
    
    if fnname == 'ls':
        resp = server.drive_api.ls(path)
    elif fnname == 'create':
        data = wiz.request.query()
        resp = server.drive_api.create(path, data)
    elif fnname == 'rename':
        data = wiz.request.query()
        resp = server.drive_api.rename(path, data)
    elif fnname == 'remove':
        data = wiz.request.query()
        resp = server.drive_api.remove(path, data)
    elif fnname == 'upload':
        filepath = wiz.request.query("filepath", "[]")
        filepath = json.loads(filepath)
        files = wiz.request.files()
        for i in range(len(files)):
            f = files[i]
            fd = (f.filename, f.stream, f.content_type, f.headers)
            fdd = dict()
            if len(filepath) > 0: 
                fdd['filepath'] = filepath[i]
            server.drive_api.upload(path, method=request.method, files={"file": fd}, data=fdd)
        wiz.response.status(200)
    elif fnname == 'download':
        resp = server.drive_api.download(path)

    if resp is None:
        wiz.response.status(404)
    
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
    response = Response(resp.content, resp.status_code, headers)
    wiz.response.response(response)


# Cron API
def cron_list():
    try:
        res = []
        user_id = wiz.session.get("id")
        cron  = CronTab(user=user_id)
        for job in cron:
            time = " ".join([str(x) for x in job.slices])
            comment = job.comment.split(";")
            wpid = comment[0]
            if wpid == workflow_id:
                comment = ";".join(comment[1:])
                res.append(dict(comment=comment, time=time))
    except Exception as e:
        wiz.response.status(500, e)
    wiz.response.status(200, res)

def cron_remove():
    try:
        comment = wiz.request.query("comment", True)
        comment = f"{workflow_id};{comment}"
        user_id = wiz.session.get("id")
        cron  = CronTab(user=user_id)
        rows = cron.find_comment(comment)
        for job in rows:
            job.enable(False)
            cron.remove(job)
        cron.write()
    except Exception as e:
        wiz.response.status(500, e)
    wiz.response.status(200)

def cron_add():
    try:
        config = wiz.config("config")
        host = urllib.parse.urlparse(wiz.request.request().base_url)
        host = f"{host.scheme}://{host.netloc}"
        if config.host:
            host = config.host
        host = f"{host}/dizest/api/cron"

        comment = wiz.request.query("comment", True)
        comment = f"{workflow_id};{comment}"

        time = wiz.request.query("time", True)
        spec = wiz.request.query("spec", True)
        user_id = wiz.session.get("id")

        cron  = CronTab(user=user_id)
        command = f'curl "{host}?user_id={user_id}&workflow_id={workflow_id}&server_id={server_id}&dbname={namespace}&spec={spec}"'
        job = cron.new(command=command, comment=comment)
        job.setall(time)
        cron.write()
        job.enable()
    except Exception as e:
        wiz.response.status(500, e)
    wiz.response.status(200)

# UI Mode
def api(segment):
    segment = segment.path.split("/")
    namespace = segment[0]
    workflow_id = segment[1]
    user = wiz.session.get("id")
    server_id = namespace + "-" + user
    db = wiz.model("orm").use(namespace)
    server = wiz.model("dizest").load(server_id).server(user=user)
    workflow = server.workflow_by_id(workflow_id)

    flow_id = segment[2]
    fnname = "/".join(segment[3:])
    flow = workflow.flow(flow_id)    
    request = wiz.request.request()
    resp = flow.api(fnname, \
        method=request.method, \
        headers={key: value for (key, value) in request.headers if key != 'Host'}, \
        data=request.values, \
        cookies=request.cookies, \
        files=request.files)

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
    response = Response(resp.content, resp.status_code, headers)
    
    wiz.response.response(response)

def render(segment):
    segment = segment.path.split("/")
    namespace = segment[0]
    workflow_id = segment[1]
    user = wiz.session.get("id")
    server_id = namespace + "-" + user
    db = wiz.model("orm").use(namespace)
    server = wiz.model("dizest").load(server_id).server(user=user)
    workflow = server.workflow_by_id(workflow_id)

    flow_id = segment[2]
    url = "/".join(wiz.request.uri().split("/")[:4] + ['api', namespace, workflow_id, flow_id])
    flow = workflow.flow(flow_id)
    app = flow.app()

    headjs = '''
    <script type="text/javascript">
    let _log = console.log;
    
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
    }

    console.log = function() {
        let style = Style.base.join(';') + ';';
        style += Style.base.join(';');
        _log(`%cdizest.js`, style, ...arguments);
    }

    window.API = (()=> {
        let obj = {};
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
    </script>
    '''.replace('{url}', url)

    pugconfig = dict()
    pugconfig['variable_start_string'] = '{[#$'
    pugconfig['variable_end_string'] = '$#]}'

    pug = app.get("pug", "")
    pug = pypugjs.Parser(pug)
    pug = pug.parse()
    pug = jinja.Compiler(pug, **pugconfig).compile()

    head = app.get("head", "")
    head = pypugjs.Parser(head)
    head = head.parse()
    head = jinja.Compiler(head, **pugconfig).compile()

    js = app.get("js")
    if js is None or len(js) == 0:
        js = ""
    else:
        js = f"<script type='text/javascript'>{js}</script>"

    css = app.get("css")
    try:
        css = sass.compile(string=css)
        css = str(css)
        css = f"<style>{css}</style>"
    except Exception as e:
        css = ""

    view = f"<!DOCTYPE html><html><head>{head}{headjs}{css}</head><body>{pug}{js}</body></html>"
    wiz.response.send(view, content_type="text/html")