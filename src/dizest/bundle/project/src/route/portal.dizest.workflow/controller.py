import season
import os
import math
import json
import time
import datetime
import shutil
import zipfile
import tempfile

Kernel = wiz.model("portal/dizest/kernel")
config = wiz.model("portal/dizest/config")
segment = wiz.request.match("/api/dizest/workflow/<zone>/<path:path>")
zone = segment.zone
action = segment.path

if config.acl(wiz, zone) == False:
    wiz.response.status(401)

fs = season.util.os.FileSystem(config.storage_path(wiz, zone))
kernel = Kernel(zone)

if action == "active":
    workflows = kernel.workflows()
    wiz.response.status(200, workflows)

workflow_id = wiz.request.query("workflow_id", True)
workflow = kernel.workflow(workflow_id)

def driveItem(path):
    def convert_size():
        size_bytes = os.path.getsize(fs.abspath(path)) 
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])

    item = dict()
    item['id'] = path
    item['type'] = 'folder' if fs.isdir(path) else 'file'
    item['title'] = os.path.basename(path)
    item['root_id'] = os.path.dirname(path)
    item['created'] = datetime.datetime.fromtimestamp(os.stat(fs.abspath(path)).st_ctime).strftime('%Y-%m-%d %H:%M:%S')
    item['modified'] = datetime.datetime.fromtimestamp(os.stat(fs.abspath(path)).st_mtime).strftime('%Y-%m-%d %H:%M:%S')
    item['size'] = convert_size()
    item['sizebyte'] = os.path.getsize(fs.abspath(path)) 
    return item

if action == "load":
    data = workflow.data()
    status = workflow.status()
    
    if status != 'stop':
        flow_status = workflow.flow.status()
        for key in data['flow']:
            try:
                del data['flow'][key]['status']
                del data['flow'][key]['index']
                del data['flow'][key]['log']
            except:
                pass
            if key in flow_status:
                data['flow'][key]['status'] = flow_status[key]['status']
                data['flow'][key]['index'] = flow_status[key]['index']
                data['flow'][key]['log'] = "<br>".join(flow_status[key]['log'])
            else:
                data['flow'][key]['status'] = 'idle'
                data['flow'][key]['index'] = -1
                data['flow'][key]['log'] = ""

    wiz.response.status(200, workflow=data, status=status)

if action == "update":
    data = json.loads(wiz.request.query("data", True))
    res = workflow.update(data)
    wiz.response.status(200, res)

if action == "status":
    status = workflow.status()
    wiz.response.status(200, status)

if action == "start":
    workflow.start()
    wiz.response.status(200)

if action == "kill":
    workflow.kill()
    wiz.response.status(200)

if action == "restart":
    workflow.restart()
    wiz.response.status(200)

if action == "run":
    workflow.run()
    wiz.response.status(200)

if action == "stop":
    workflow.stop()
    wiz.response.status(200)

if action == "flow/run":
    flow_id = wiz.request.query("flow_id")
    res = workflow.flow.run(flow_id)
    wiz.response.status(res.code)

if action == "flow/stop":
    flow_id = wiz.request.query("flow_id")
    res = workflow.flow.stop(flow_id)
    wiz.response.status(res.code)

if action == "spec":
    wiz.response.status(200, workflow.spec())

if action == "spec/update":
    spec = wiz.request.query("spec", True)
    specdata = kernel.spec(spec)
    if specdata['name'] == spec:
        workflow.set(spec=spec)
    wiz.response.status(200)

if action == "drive/list":
    path = wiz.request.query("path", "")
    scanparent = wiz.request.query("scanparent", None)
    if scanparent is not None:
        path = os.path.dirname(path)

    basedir = os.path.dirname(workflow_id)
    basedir = os.path.join(basedir, path)
    files = fs.ls(basedir)
    res = []
    for f in files:
        fi = driveItem(os.path.join(basedir, f))
        fi['id'] = os.path.join(path, f)
        res.append(fi)

    parent = None
    if len(path) > 0:
        parent = os.path.dirname(path)
    
    wiz.response.status(200, parent=parent, files=res)

wiz.response.status(404)